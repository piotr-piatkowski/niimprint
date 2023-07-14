import os
import argparse
import printerclient
import printencoder

from PIL import Image, ImageDraw, ImageFont
import time

# import math
# mm_to_px = lambda x: math.ceil(x / 25.4 * 203)
# px_to_mm = lambda x: math.ceil(x / 25.4 * 203)

def create_label(args):
    w = args.width
    h = args.height
    img = Image.new('1', (w, h), 1)
    draw = ImageDraw.Draw(img)
    font_size = args.font_size
    font_name = 'DejaVuSans-Bold.ttf' if args.bold else 'DejaVuSans.ttf'
    txt = args.text

    if font_size == 0:
        font_size = 42
        while font_size > 5:        
            font = ImageFont.truetype(font_name, font_size)
            bbox = draw.textbbox((w//2, h//2), txt, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            if tw <= w - 4 and th <= h - 4:
                break
            font_size -= 1
        print(f"Using font size {font_size}")
    else:
        font = ImageFont.truetype(font_name, font_size)

    draw.text((w//2, h//2), txt, font=font, fill=0, anchor="mm")
    return img

def get_test_image(w, h):
    img = Image.new('1', (w, h), 1)
    draw = ImageDraw.Draw(img)
    for x in range(0, w, 10):
        for y in range(0, h, 10):
            draw.line((x, 0, x, h), fill=0)
            if x % 50 == 0:
                draw.line((x-1, 0, x-1, h), fill=0)
                draw.line((x+1, 0, x+1, h), fill=0)
            draw.line((0, y, w, y), fill=0)
            if y % 50 == 0:
                draw.line((0, y-1, w, y-1), fill=0)
                draw.line((0, y+1, w, y+1), fill=0)

    font = ImageFont.truetype('DejaVuSans-Bold.ttf', 42)
    draw.text((w//2, h//2), 'Hello, world!', font=font,
               fill=0, stroke_fill=1, stroke_width=3, anchor="mm")
    return img

def run_ui(args, img):
    import PySimpleGUI as sg
    from io import BytesIO

    sg.theme('SystemDefault')

    img_io = BytesIO()
    img.save(img_io, format='PNG')

    layout = [
        [
            sg.Text('Text: '),
            sg.InputText(args.text, key="input", enable_events=True),
        ],
        [
            sg.Checkbox('Bold', enable_events=True, key="bold",
                        default=args.bold),
            sg.Text('Font size: '),
            sg.Slider((5, 99), key="font_size", default_value=args.font_size,
                      orientation='h', enable_events=True),
        ],
        [
            sg.Frame("Preview:", [
                [sg.Image(key="image_preview", data=img_io.getvalue())]
            ])
        ],
        [sg.Button('Quit'), sg.Button('Print')],
    ]
    window = sg.Window('Niimbot Printer Client', layout)

    def update_image(values):
        nonlocal img
        args.bold = values['bold']
        args.font_size = values['font_size']
        args.text = values['input']
        img = create_label(args)
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        window['image_preview'].update(data=img_io.getvalue())

    while True:
        event, values = window.read()
        print(f"Event: {event}, Values: {values}")
        if event in (None, 'Quit'):
            break
        elif event in ('input', 'font_size', 'bold'):
            update_image(values)
        elif event == 'Print':
            print("Printing...")


if __name__ == '__main__':

    address = os.environ.get('NIIMBOT_ADDRESS', None)

    parser = argparse.ArgumentParser(
        description="Niimbot printer client")
    parser.add_argument('-a', '--address', required=(address is None),
                        default=address,
                        help="MAC address of target device")
    parser.add_argument('--no-check', action='store_true',
                        help="Skips image check")
    parser.add_argument('-d', '--density', type=int, default=2,
                        help="Printer density (1~3)")
    parser.add_argument('-t', '--type', type=int, default=1,
                        help="Label type (1~3)")
    parser.add_argument('-n', '--quantity', type=int, default=1,
                        help="Number of copies")
    parser.add_argument('--test-image', '-ti', action='store_true',
                        help="Use test image instead of file")
    parser.add_argument('--show-only', '-so', action='store_true',
                        help="Don't print, but show image")
    parser.add_argument('--ui', '-ui', action='store_true',
                        help="Display UI with image preview")
    parser.add_argument('--text', '-T', type=str,
                        help='Text to print')
    parser.add_argument('-W', '--width', type=int, default=320,
                        help="Width of the image")
    parser.add_argument('-H', '--height', type=int, default=96,
                        help="Height of the image")
    parser.add_argument('--bold', '-b', action='store_true',
                        help="Use bold font")
    parser.add_argument('--font-size', '-fs', type=int, default=0,
                        help="Font size, 0 for auto")
    parser.add_argument('image', nargs='?', help="PIL supported image file")
    args = parser.parse_args()

    if args.test_image:
        img = get_test_image(320, 96)
    elif args.text:
        img = create_label(args)
    elif args.image is None:
        parser.print_help()
        exit(1)
    else:
        img = Image.open(args.image)
        if img.width / img.height < 1:
            # rotate clockwise 90deg, upper line (left line) prints first.
            img = img.transpose(Image.ROTATE_90)
        assert args.no_check or (img.width < 600 and img.height == 96)

    if args.ui:
        run_ui(args, img)
        exit(0)

    if args.show_only:
        img.show()
        exit(0)

    img = img.transpose(Image.ROTATE_270)

    printer = printerclient.PrinterClient(args.address)
    printer.set_label_type(args.type)
    printer.set_label_density(args.density)

    printer.start_print()
    printer.allow_print_clear()
    printer.start_page_print()
    printer.set_dimension(img.height, img.width)
    printer.set_quantity(args.quantity)
    for pkt in printencoder.naive_encoder(img):
        printer._send(pkt)
    printer.end_page_print()
    while (a := printer.get_print_status())['page'] != args.quantity:
        # print(a)
        time.sleep(0.1)
    printer.end_print()
