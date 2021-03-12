

class Format:
    ALLOWED_TYPES = 'fd'
    RGX_ESCAPE = '+*?[]()^$|.'

    def __init__(self, format: str):
        self.format = format
        self.extract_params(format)
        self.expression = self.generate_expression()

    def extract_params(self, format):
        self.align = None
        self.fill = ' '
        if format[0] in '<>=^':
            self.align = format[0]
            format = format[1:]
        elif len(format) > 1 and format[1] in '<>=^':
            self.fill = format[0]
            self.align = format[1]
            format = format[2:]

        self.sign = '-'
        if format and format[0] in '+- ':
            self.sign = format[0]
            format = format[1:]

        self.alternate = False
        if format and format[0] == '#':
            self.alternate = True
            format = format[1:]

        self.zero = False
        if format and format[0] == '0':
            self.zero = True
            format = format[1:]

        self.width = ''
        while format:
            if not format[0].isdigit():
                break
            self.width += format[0]
            format = format[1:]
        if self.width == '':
            self.width = 0
        self.width = int(self.width)

        self.grouping = None
        if format and format[0] in '_,':
            self.grouping = format[0]
            format = format[1:]

        self.precision = ''
        if format.startswith('.'):
            # Precision isn't needed but we need to capture it so that
            # the ValueError isn't raised.
            format = format[1:]  # drop the '.'
            while format:
                if not format[0].isdigit():
                    break
                self.precision += format[0]
                format = format[1:]
        if self.precision:
            self.precision = int(self.precision)

        self.type = format
        if not self.type or self.type not in self.ALLOWED_TYPES:
            raise ValueError('format spec %r not supported' % self.type)

    @classmethod
    def escape(cls, char: str) -> str:
        if len(char) > 1:
            raise IndexError("String to escape longer than one character")
        if char in cls.RGX_ESCAPE:
            return r'\{}'.format(char)
        return char

    def generate_expression(self):
        if self.type == 'f':
            return self.generate_expression_f()
        if self.type == 'd':
            return self.generate_expression_d()

    def generate_expression_d(self):
        rgx = ''
        rgx += self.get_sign()
        rgx += self.get_align()
        rgx += self.get_left_point()
        return rgx

    def generate_expression_f(self):
        rgx = ''
        rgx += self.get_sign()
        rgx += self.get_align()
        rgx += self.get_left_point()

        if self.precision == '':
            self.precision = 6
        if self.precision != 0 or self.alternate:
            rgx += r'\.'
        rgx += r'\d{{{}}}'.format(self.precision)

        return rgx

    def get_sign(self):
        if self.sign == '-':
            rgx = '-?'
        elif self.sign == '+':
            rgx = r'(?:\+|-)'
        elif self.sign == ' ':
            rgx = r'(?:\s|-)'
        else:
            raise KeyError("Sign not in {+- }")
        return rgx

    def get_align(self):
        if self.align is not None and self.align in '<>^':
            raise KeyError("Align <>^ not supported")

        rgx = ''
        if self.width and self.width > 0:
            if self.zero:
                self.fill = '0'
            rgx += '{}*'.format(self.escape(self.fill))

        return rgx

    def get_left_point(self):
        if self.grouping is not None:
            rgx = r'\d?\d?\d(?:{}\d{{3}})*'.format(self.grouping)
        else:
            rgx = r'\d*'
        return rgx
