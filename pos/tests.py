from django.http import JsonResponse ,HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Sequence ,PrinterPreference
import usb.core
import usb.util
from django.shortcuts import render, redirect


def home(request):
    return render(request, "sequence.html")





@csrf_exempt  # For demonstration purposes only, consider CSRF in production
@require_http_methods(["POST"])
def sequence_view(request):
    number_to_print = request.POST.get('number_to_print')
    print_next = 'print_next' in request.POST

    if 'reset' in request.POST:
        # Reset sequence number
        Sequence.objects.update(number=0)
        return JsonResponse({'number': 0, 'status': 'Sequence reset'})
    
    sequence = Sequence.objects.get(id=1)

    if print_next:
        # Increment and save the sequence number
        sequence.number += 1

        sequence.save()

    elif number_to_print:
        try:
            # Convert number to integer
            number_to_print = int(number_to_print)
            # Update the sequence number with the provided value
            sequence.number = number_to_print
            sequence.save()
        except ValueError:
            # Handle the case where the input is not a valid integer
            return JsonResponse({'status': 'Invalid number'}, status=400)

    # Call print_sequence and expect a dictionary in response
    response = print_sequence(sequence.number)
    
    # Include the response from print_sequence in the JsonResponse
    return JsonResponse({'number': sequence.number, **response})




def print_sequence(number):

    # Initialize printer (ESC @)
    data = b'\x1b\x40'

    # Print a title in double size
    data += b'\x1b\x21\x30'  # ESC ! n -- Select print mode for double height and width
    data += 'ROADLINKS MIDLLE EAST\n'.encode('utf-8')

    # Reset to normal size text
    data += b'\x1b\x21\x00'  # ESC ! n -- Cancel character size
    data += 'FORWARD\nRegistration\n'.encode('utf-8')

    # Reset to normal size text
    data += b'\x1b\x21\x10'  # ESC ! n -- Select print mode for double height and width
    data += 'INFO : \n'.encode('utf-8')

    # Draw a horizontal line or border
    data += b'\x1b\x21\x00'  # ESC ! n -- Select print mode for double height and width

    data += b'--------------------------------\n'

    # Token number in large size
    data += b'\x1b\x21\x30'  # ESC ! n -- Select print mode for double height and width
    data += 'TOKEN NO:{}\n'.format(number).encode('utf-8')

    # Reset to normal size text
    data += b'\x1b\x21\x10'  # ESC ! n -- Cancel character size

    # Cut the paper with a partial cut (GS V m)
    data += b'\x1d\x56\x42\x00'  # GS V m -- Cut the paper with a partial cut
    
    try:
        # Fetch the default printer preference from the database
        default_printer = PrinterPreference.objects.filter(is_default=True).first()
        if not default_printer:
            return "No default printer selected."
        
        # Split the device ID to get vendor and product IDs
        vendor_id, product_id = map(lambda x: int(x, 16), default_printer.device_id.split(':'))
        
        # Find the printer using the vendor and product IDs
        dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if dev is None:
            return HttpResponse('Device not found', status=500)
        
        # Detach it from the kernel driver
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)
        
        # Claim the interface
        usb.util.claim_interface(dev, 0)
        
        # Determine the correct endpoint
        endpoint = dev[0][(0,0)][0]
        
        # Write data to the printer
        dev.write(endpoint.bEndpointAddress, data, timeout=10000)
        
        # Release the device
        usb.util.release_interface(dev, 0)
        
        # Reattach the device to the kernel driver if necessary
        dev.attach_kernel_driver(0)
        
         # If everything is successful, return a simple message or a dictionary.
        return {"message": f"Printed sequence number {number}"}
    except usb.core.USBError as e:
        # Return error details in a serializable format
        return {"error": f"Error sending data to the printer: {e}"}
    except Exception as e:
        # Return error details in a serializable format
        return {"error": f"An error occurred: {e}"}



def list_usb_devices(request):
    devices = list(usb.core.find(find_all=True))
    if request.method == 'POST':
        selected_device_id = request.POST.get('device_id')
        selected_device = next((d for d in devices if f"{d.idVendor}:{d.idProduct}" == selected_device_id), None)

        if selected_device:
            device_name = "Unknown Device"  # Default device name
            try:
                device_name = selected_device.product
            except ValueError:
                pass  # Ignore the error and use the default device name

            PrinterPreference.objects.all().update(is_default=False)  # Mark all as not default
            PrinterPreference.objects.update_or_create(
                device_id=selected_device_id,
                defaults={'device_name': device_name, 'is_default': True}
            )
            return redirect('pos:home')  # Redirect to home or another appropriate view

    device_list = []
    for device in devices:
        device_id = f"{device.idVendor}:{device.idProduct}"
        device_name = "Unknown Device"  # Default device name
        try:
            if device.product is not None:
                device_name = device.product
        except ValueError:
            pass  # Ignore the error and use the default device name
        device_list.append({'id': device_id, 'name': device_name})

    return render(request, 'list_usb_devices.html', {'devices': device_list})
