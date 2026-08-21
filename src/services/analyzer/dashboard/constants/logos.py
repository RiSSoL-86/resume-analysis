from typing import Final

_MONO: Final = (
    '<svg class="brand" viewBox="0 0 40 40" aria-hidden="true">'
    '<rect width="40" height="40" fill="{bg}"/>'
    '<text x="20" y="{y}" text-anchor="middle" font-family="Arial,Helvetica,'
    'sans-serif" font-size="{fs}" font-weight="900" fill="{fg}">{txt}</text>'
    "</svg>"
)
_SBER_SVG: Final = (
    '<svg class="brand" viewBox="0 0 40 40" aria-hidden="true">'
    '<rect width="40" height="40" fill="#21a038"/>'
    '<path d="M29 13.5a10 10 0 1 0 2.6 6" fill="none" stroke="#fff" '
    'stroke-width="3.4" stroke-linecap="round"/>'
    '<path d="M14.5 20l4.2 4 8.3-9" fill="none" stroke="#fff" '
    'stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)
COMPANY_LOGOS: Final = {
    "sbertech": _SBER_SVG,
    "сбер": _SBER_SVG,
    "sber": _SBER_SVG,
    "ecom": _MONO.format(bg="#1b1c22", fg="#fff", txt="e.", fs=19, y=27),
    "джет": _MONO.format(bg="#2b3a8c", fg="#fff", txt="jet", fs=15, y=26),
    "тинькоф": _MONO.format(bg="#ffdd2d", fg="#1a1a1a", txt="Т", fs=21, y=28),
    "tinkoff": _MONO.format(bg="#ffdd2d", fg="#1a1a1a", txt="Т", fs=21, y=28),
    "альфа": _MONO.format(bg="#ef3124", fg="#fff", txt="А", fs=21, y=28),
    "alfa": _MONO.format(bg="#ef3124", fg="#fff", txt="A", fs=21, y=28),
    "яндекс": _MONO.format(bg="#fff", fg="#fc3f1d", txt="Я", fs=21, y=28),
    "yandex": _MONO.format(bg="#fff", fg="#fc3f1d", txt="Я", fs=21, y=28),
    "ozon": _MONO.format(bg="#005bff", fg="#fff", txt="O", fs=21, y=28),
    "озон": _MONO.format(bg="#005bff", fg="#fff", txt="O", fs=21, y=28),
    "vk": _MONO.format(bg="#0077ff", fg="#fff", txt="VK", fs=15, y=26),
    "втб": _MONO.format(bg="#002882", fg="#fff", txt="втб", fs=13, y=25),
    "vtb": _MONO.format(bg="#002882", fg="#fff", txt="втб", fs=13, y=25),
    "мтс": _MONO.format(bg="#e30611", fg="#fff", txt="МТС", fs=12, y=25),
    "mts": _MONO.format(bg="#e30611", fg="#fff", txt="МТС", fs=12, y=25),
}
