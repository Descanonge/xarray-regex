

ALLOWED_TYPES = 'fds'
RGX_ESCAPE = '+*?[]()^$|.'


def extract_params(format):
    align = None
    fill = None
    if format[0] in '<>=^':
        align = format[0]
        format = format[1:]
    elif len(format) > 1 and format[1] in '<>=^':
        fill = format[0]
        align = format[1]
        format = format[2:]

    sign = '-'
    if format and format[0] in '+- ':
        sign = format[0]
        format = format[1:]

    alternate = False
    if format and format[0] == '#':
        alternate = True
        format = format[1:]

    zero = False
    if format and format[0] == '0':
        zero = True
        if align is None:
            align = '='
        if fill is None:
            fill = '0'
        format = format[1:]
    if fill is None:
        fill = ' '

    width = ''
    while format:
        if not format[0].isdigit():
            break
        width += format[0]
        format = format[1:]
    if width == '':
        width = 0
    width = int(width)

    grouping = None
    if format and format[0] in '_,':
        grouping = format[0]
        format = format[1:]

    precision = ''
    if format.startswith('.'):
        # Precision isn't needed but we need to capture it so that
        # the ValueError isn't raised.
        format = format[1:]  # drop the '.'
        while format:
            if not format[0].isdigit():
                break
            precision += format[0]
            format = format[1:]
    if precision:
        precision = int(precision)

    type = format
    if not type or type not in ALLOWED_TYPES:
        raise ValueError('format spec %r not supported' % type)

    return locals()


def escape(char: str) -> str:
    if len(char) > 1:
        raise IndexError("String to escape longer than one character")
    if char in RGX_ESCAPE:
        return r'\{}'.format(char)
    return char


def generate_expression(format):
    params = extract_params(format)
    if params['type'] == 'f':
        return generate_expression_f(params)
    if params['type'] == 'd':
        return generate_expression_d(params)
    if params['type'] == 's':
        return generate_expression_s(params)


def generate_expression_s(params):
    return '.*?'


def generate_expression_d(params):
    if params['align'] is None:
        params['align'] = '>'

    rgx = ''
    align, loc = get_align(*[params[p] for p in ['align', 'width', 'fill']])
    if loc in ['left', 'center']:
        rgx += align

    rgx += get_sign(params['sign'])

    if loc == 'middle':
        rgx += align

    rgx += get_left_point(params['grouping'])

    if loc in ['right', 'center']:
        rgx += align

    return rgx


def generate_expression_f(params):
    if params['align'] is None:
        params['align'] = '>'

    rgx = ''
    align, loc = get_align(*[params[p] for p in ['align', 'width', 'fill']])

    if loc in ['left', 'center']:
        rgx += align

    rgx += get_sign(params['sign'])

    if loc == 'middle':
        rgx += align

    rgx += get_left_point(params['grouping'])

    precision = params['precision']
    if precision == '':
        precision = 6
    if precision != 0 or params['alternate']:
        rgx += r'\.'
    rgx += r'\d{{{}}}'.format(precision)

    if loc in ['right', 'center']:
        rgx += align

    return rgx


def get_sign(sign):
    if sign == '-':
        rgx = '-?'
    elif sign == '+':
        rgx = r'(?:\+|-)'
    elif sign == ' ':
        rgx = r'(?:\s|-)'
    else:
        raise KeyError("Sign not in {+- }")
    return rgx


def get_align(align, width, fill):
    rgx = ''
    if width and width > 0:
        rgx += '{}*'.format(escape(fill))

    loc = {
        '=': 'middle',
        '>': 'left',
        '<': 'right',
        '^': 'center'
    }[align]

    return rgx, loc


def get_left_point(grouping):
    if grouping is not None:
        rgx = r'\d?\d?\d(?:{}\d{{3}})*'.format(grouping)
    else:
        rgx = r'\d*'
    return rgx
