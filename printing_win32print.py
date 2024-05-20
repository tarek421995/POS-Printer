import win32print
import win32ui
import win32con

def print_to_oscar(printer_name, token_number):
    # Open the printer
    printer_handle = win32print.OpenPrinter(printer_name)

    try:
        # Start a print job
        job_info = ("Token Print", None, "RAW")
        job_id = win32print.StartDocPrinter(printer_handle, 1, job_info)
        win32print.StartPagePrinter(printer_handle)

        # Initialize printer (ESC @)
        data = b'\x1b\x40'
        data += b'\x1b\x37\x06\x15\x10'  # ESC 7 - Set heating parameters for dark, high-quality prints    

        # Print a title in double size
        data += b'\x1b\x21\x30'  # ESC ! n -- Select print mode for double height and width
        data += 'Your Company Name\n'.encode('utf-8')

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
        data += 'TOKEN NO:{}\n'.format(token_number).encode('utf-8')

        # Reset to normal size text
        data += b'\x1b\x21\x10'  # ESC ! n -- Cancel character size

        # Cut the paper with a partial cut (GS V m)
        data += b'\x1d\x56\x42\x00'  # GS V m -- Cut the paper with a partial cut

        # Try to disable the beeper
        data += b'\x1B\x42\x00\x00'  # ESC B 0 0 -- Attempt to disable the beeper

        # Send the data to the printer
        win32print.WritePrinter(printer_handle, data)

        # End the print job
        win32print.EndPagePrinter(printer_handle)
        win32print.EndDocPrinter(printer_handle)
    finally:
        # Close the printer
        win32print.ClosePrinter(printer_handle)

if __name__ == "__main__":
    printer_name = "OSCAR POS88C (USB)"
    token_number = 123  # Example token number
    print_to_oscar(printer_name, token_number)
