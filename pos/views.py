from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Sequence, PrinterPreference
import win32print
import win32com.client
import pythoncom
import logging

def home(request):
    return render(request, "sequence.html")

@csrf_exempt  # For demonstration purposes only, consider CSRF in production
@require_http_methods(["POST"])
def sequence_view(request):
    number_to_print = request.POST.get('number_to_print')
    print('number_to_print', number_to_print)
    if 'reset' in request.POST:
        # Reset sequence number
        Sequence.objects.update(number=0)
        return JsonResponse({'number': 0, 'status': 'Sequence reset'})
    
    sequence = Sequence.objects.get(id=1)

    if number_to_print:
        try:
            # Convert number to integer
            number_to_print = int(number_to_print)
            # Update the sequence number with the provided value
            sequence.number = number_to_print
            sequence.save()
            print('sequence.number, number_to_print', sequence.number, number_to_print)

            response = print_sequence(sequence.number)
            return JsonResponse({'number': number_to_print, 'status': 'Sequence Setting Success', **response})

        except ValueError:
            # Handle the case where the input is not a valid integer
            return JsonResponse({'status': 'Invalid number'}, status=400)
    else:
        # Increment and save the sequence number
        sequence.number += 1
        sequence.save()
        response = print_sequence(sequence.number)

    return JsonResponse({'number': sequence.number, **response})

def print_sequence(number):
    print('tarek')
    # Initialize printer (ESC @)
    data = b'\x1b\x40'
    data += b'\x1b\x37\x06\x15\x10'  # ESC 7 - Set heating parameters for dark, high-quality prints    

    # Print a title in double size
    data += b'\x1b\x21\x30'  # ESC ! n -- Select print mode for double height and width
    data += 'Your comany name\n'.encode('utf-8')

    # Reset to normal size text
    data += b'\x1b\x21\x00'  # ESC ! n -- Cancel character size
    data += 'Registration\n'.encode('utf-8')

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

    # Try to disable the beeper
    data += b'\x1B\x42\x00\x00'  # ESC B 0 0 -- Attempt to disable the beeper

    try:
        # Fetch the default printer preference from the database
        default_printer = PrinterPreference.objects.filter(is_default=True).first()
        print('default_printer', default_printer)
        if not default_printer:
            return {"status": "error", "message": "No default printer selected."}
        
        printer_name = default_printer.device_name
        print('printer_name', printer_name)

        # Use win32print to send data to the printer
        printer_handle = win32print.OpenPrinter(printer_name)

        try:
            job_info = ("Token Print", None, "RAW")
            job_id = win32print.StartDocPrinter(printer_handle, 1, job_info)
            win32print.StartPagePrinter(printer_handle)
            win32print.WritePrinter(printer_handle, data)
            win32print.EndPagePrinter(printer_handle)
            win32print.EndDocPrinter(printer_handle)
        finally:
            win32print.ClosePrinter(printer_handle)

        return {"status": "success", "message": f"Printed sequence number {number}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}

logging.basicConfig(level=logging.DEBUG)

def list_devices():
    try:
        pythoncom.CoInitialize()
        logging.debug("Attempting to connect to WMI service...")
        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        wmi_service = wmi.ConnectServer(".", "root\cimv2")
        logging.debug("Connected to WMI service.")
        devices = wmi_service.ExecQuery("SELECT * FROM Win32_PnPEntity")
        device_list = [{'device_name': device.Name} for device in devices]
        return device_list
    except pythoncom.com_error as e:
        logging.error(f"Failed to get WMI object: {e}")
        return [{'error': 'Failed to list devices due to a WMI error.'}]
    finally:
        pythoncom.CoUninitialize()


@csrf_exempt  # For demonstration purposes only, consider CSRF in production
@require_http_methods(["GET", "POST"])
def list_usb_devices(request):
    if request.method == "POST":
        default_printer_name = request.POST.get('default_printer')
        if default_printer_name:
            # Set all printers to not default
            all_printers = PrinterPreference.objects.all().update(is_default=False)
            our_printer, created = PrinterPreference.objects.get_or_create(device_name=default_printer_name)
            if our_printer:
                our_printer.is_default =True
                our_printer.save()
            # Set the selected printer as default
            return redirect('pos:home')  # Use the correct namespace here

    device_list = list_devices()
    if not device_list:
        device_list = [{'error': f"No USB devices found."}]
    logging.debug(f'device_list: {device_list}')
    return render(request, 'list_usb_devices.html', {'devices': device_list})