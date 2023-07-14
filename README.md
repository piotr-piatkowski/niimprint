usage: niimprint [-h] [-a ADDRESS] [--no-check] [-d DENSITY] [-t TYPE]
                 [-n QUANTITY] [--test-image] [--show-only] [--ui]
                 [--text TEXT] [-W WIDTH] [-H HEIGHT] [--bold]
                 [--font-size FONT_SIZE]
                 [image]

Niimbot printer client

positional arguments:
  image                 PIL supported image file

options:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        MAC address of target device
  --no-check            Skips image check
  -d DENSITY, --density DENSITY
                        Printer density (1~3)
  -t TYPE, --type TYPE  Label type (1~3)
  -n QUANTITY, --quantity QUANTITY
                        Number of copies
  --test-image, -ti     Use test image instead of file
  --show-only, -so      Don't print, but show image
  --ui, -ui             Display UI with image preview
  --text TEXT, -T TEXT  Text to print
  -W WIDTH, --width WIDTH
                        Width of the image
  -H HEIGHT, --height HEIGHT
                        Height of the image
  --bold, -b            Use bold font
  --font-size FONT_SIZE, -fs FONT_SIZE
                        Font size, 0 for auto
