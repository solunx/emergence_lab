"""ASCII and raster frames. Does not touch experiment RNGs."""

from __future__ import annotations

from PIL import Image, ImageDraw

from emergence_lab.world.world import WorldState

PALETTE = [
    (220, 70, 70),
    (70, 140, 220),
    (240, 180, 50),
    (80, 200, 140),
    (180, 90, 220),
    (50, 200, 200),
    (230, 120, 80),
    (140, 200, 70),
    (230, 80, 160),
    (90, 110, 210),
]


def organism_color(organism_id: int) -> tuple[int, int, int]:
    return PALETTE[organism_id % len(PALETTE)]


def render_ascii(state: WorldState) -> str:
    grid = [["." for _ in range(state.width)] for _ in range(state.height)]
    for site in state.sites:
        char = "F" if site.has_food else ","
        # Print row 0 as north (y = height-1).
        row = state.height - 1 - site.y
        grid[row][site.x] = char
    for org in state.living():
        row = state.height - 1 - org.y
        grid[row][org.x] = str(org.id % 10)
    header = f"Tick: {state.tick}  Population: {len(state.living())}"
    body = "\n".join("".join(row) for row in grid)
    return f"{header}\n{body}"


def render_image(state: WorldState, cell: int = 10) -> Image.Image:
    width = state.width * cell
    height = state.height * cell
    image = Image.new("RGB", (width, height), (18, 20, 24))
    draw = ImageDraw.Draw(image)
    for site in state.sites:
        x0 = site.x * cell
        y0 = (state.height - 1 - site.y) * cell
        pad = max(1, cell // 5)
        box = [x0 + pad, y0 + pad, x0 + cell - pad - 1, y0 + cell - pad - 1]
        if box[2] < box[0] or box[3] < box[1]:
            box = [x0, y0, x0 + cell - 1, y0 + cell - 1]
        if site.has_food:
            draw.rectangle(box, fill=(80, 190, 90))
        else:
            draw.rectangle(box, outline=(40, 80, 45))
    for org in state.living():
        x0 = org.x * cell
        y0 = (state.height - 1 - org.y) * cell
        pad = max(0, cell // 8)
        color = organism_color(org.id)
        draw.ellipse(
            [x0 + pad, y0 + pad, x0 + cell - pad - 1, y0 + cell - pad - 1],
            fill=color,
        )
    return image


WHITE = (255, 255, 255)
BANNER = (16, 18, 22)


def _draw_banner(draw: ImageDraw.ImageDraw, box: list[int], text: str) -> None:
    draw.rectangle(box, fill=BANNER)
    x0, y0, _x1, _y1 = box
    draw.text((x0 + 4, y0 + 3), text, fill=WHITE)


def render_panel(
    state: WorldState,
    *,
    tick: int,
    label: str | None = None,
    cell: int = 8,
    banner: int = 16,
) -> Image.Image:
    """World raster with a tick banner, optional controller label, white 1px border."""
    world = render_image(state, cell=cell)
    extra = banner if not label else banner * 2
    image = Image.new("RGB", (world.width + 2, world.height + extra + 2), WHITE)
    draw = ImageDraw.Draw(image)
    y = 1
    _draw_banner(draw, [1, y, world.width, y + banner - 1], f"tick {tick}   pop {len(state.living())}")
    y += banner
    if label:
        _draw_banner(draw, [1, y, world.width, y + banner - 1], label.upper())
        y += banner
    image.paste(world, (1, y))
    return image
