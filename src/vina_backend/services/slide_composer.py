"""
Professional slide composer for TikTok-style educational videos.
Implements a complete design system with card-based layouts.
"""
import logging
from pathlib import Path
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DesignSystem:
    """
    Professional design system for vertical video slides.
    Based on mobile-first, card-based design principles.
    """
    # Canvas
    width: int = 1080
    height: int = 1920
    
    # Margins and safe areas
    margin_x: int = 80  # Left/right margins
    
    # Zones (y-coordinates)
    top_bar_start: int = 60
    top_bar_end: int = 170
    
    title_zone_start: int = 190
    title_zone_end: int = 330
    
    content_zone_start: int = 360
    content_zone_end: int = 1740
    
    bottom_bar_start: int = 1760
    bottom_bar_end: int = 1880
    
    # Typography
    title_font_size: int = 64
    body_font_size: int = 44
    label_font_size: int = 28
    logo_font_size: int = 48
    
    title_line_height: float = 1.15
    body_line_height: float = 1.25
    
    # Card styling
    card_corner_radius: int = 28
    image_card_corner_radius: int = 36
    card_padding: int = 24
    card_spacing: int = 24
    
    # Card dimensions
    card_width: int = 920  # width - 2*margin_x
    bullet_card_height_single: int = 140
    bullet_card_height_double: int = 190
    
    image_card_height: int = 760
    image_card_inner_width: int = 872  # card_width - 2*card_padding
    image_card_inner_height: int = 712  # image_card_height - 2*card_padding
    
    # Colors (modern, professional palette)
    bg_color: Tuple[int, int, int] = (15, 23, 42)  # Dark blue-gray
    card_bg_color: Tuple[int, int, int] = (30, 41, 59)  # Slightly lighter
    
    title_color: Tuple[int, int, int] = (255, 255, 255)  # White
    body_color: Tuple[int, int, int] = (203, 213, 225)  # Light gray
    accent_color: Tuple[int, int, int] = (59, 130, 246)  # Blue
    label_color: Tuple[int, int, int] = (148, 163, 184)  # Medium gray


class SlideComposer:
    """
    Professional slide composer with card-based design system.
    
    Features:
    - Two templates: Text+Image and Text-Only
    - Logo support (image or text fallback)
    - Consistent spacing and typography
    - Mobile-first, TikTok-style aesthetic
    """
    
    def __init__(
        self,
        design: Optional[DesignSystem] = None,
        logo_path: Optional[Path] = None,
        brand_name: str = "VINA"
    ):
        """
        Initialize slide composer.
        
        Args:
            design: Design system configuration
            logo_path: Path to logo image (optional)
            brand_name: Brand name for text-based logo fallback
        """
        self.design = design or DesignSystem()
        self.brand_name = brand_name
        
        # Load fonts
        self.title_font = self._load_font(self.design.title_font_size)
        self.body_font = self._load_font(self.design.body_font_size)
        self.label_font = self._load_font(self.design.label_font_size)
        self.logo_font = self._load_font(self.design.logo_font_size, bold=True)
        
        # Load logo (if available)
        self.logo = None
        if logo_path and logo_path.exists():
            try:
                self.logo = Image.open(logo_path).convert("RGBA")
                logger.info(f"Logo loaded from {logo_path}")
            except Exception as e:
                logger.warning(f"Failed to load logo: {e}")
        
        logger.info(f"Slide composer initialized ({self.design.width}x{self.design.height})")
    
    def _load_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Load system font with fallback."""
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/System/Library/Fonts/SFNSDisplay.ttf",  # macOS SF
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ]
        
        for font_path in font_paths:
            try:
                if Path(font_path).exists():
                    return ImageFont.truetype(font_path, size)
            except Exception:
                continue
        
        logger.warning(f"Using default font (size={size})")
        return ImageFont.load_default()
    
    def compose_slide(
        self,
        title: str,
        output_path: Path,
        bullets: Optional[List[str]] = None,
        image_path: Optional[Path] = None,
        slide_number: int = 1,
        total_slides: int = 1,
        course_label: Optional[str] = None
    ) -> Path:
        """
        Compose a professional slide (auto-selects template).
        
        Args:
            title: Slide title
            output_path: Where to save the slide
            bullets: List of bullet points (2-4 items)
            image_path: Path to image (if None, uses text-only template)
            slide_number: Current slide number
            total_slides: Total number of slides
            course_label: Optional course label for top-right
        
        Returns:
            Path to the composed slide
        """
        if image_path and image_path.exists():
            return self._compose_text_image_slide(
                title, output_path, bullets or [], image_path,
                slide_number, total_slides, course_label
            )
        else:
            return self._compose_text_only_slide(
                title, output_path, bullets or [],
                slide_number, total_slides, course_label
            )
    
    def _compose_text_image_slide(
        self,
        title: str,
        output_path: Path,
        bullets: List[str],
        image_path: Path,
        slide_number: int,
        total_slides: int,
        course_label: Optional[str]
    ) -> Path:
        """Text+Image template: 1 image card + 2 bullet cards."""
        logger.info(f"Composing Text+Image slide {slide_number}/{total_slides}")
        
        # Create canvas
        canvas = Image.new("RGB", (self.design.width, self.design.height), self.design.bg_color)
        draw = ImageDraw.Draw(canvas)
        
        # Draw common elements
        self._draw_top_bar(draw, course_label)
        self._draw_title(draw, title)
        self._draw_bottom_bar(draw, slide_number, total_slides)
        
        # === IMAGE CARD ===
        img_card_y = self.design.content_zone_start
        self._draw_image_card(canvas, image_path, self.design.margin_x, img_card_y)
        
        # === BULLET CARDS (max 2) ===
        bullets_to_show = bullets[:2]  # Limit to 2 for this template
        bullet_y = img_card_y + self.design.image_card_height + self.design.card_spacing
        
        for bullet in bullets_to_show:
            self._draw_bullet_card(draw, bullet, self.design.margin_x, bullet_y)
            bullet_y += self.design.bullet_card_height_single + self.design.card_spacing
        
        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path, quality=95)
        logger.info(f"Slide saved to {output_path}")
        return output_path
    
    def _compose_text_only_slide(
        self,
        title: str,
        output_path: Path,
        bullets: List[str],
        slide_number: int,
        total_slides: int,
        course_label: Optional[str]
    ) -> Path:
        """Text-Only template: 3-4 bullet cards."""
        logger.info(f"Composing Text-Only slide {slide_number}/{total_slides}")
        
        # Create canvas
        canvas = Image.new("RGB", (self.design.width, self.design.height), self.design.bg_color)
        draw = ImageDraw.Draw(canvas)
        
        # Draw common elements
        self._draw_top_bar(draw, course_label)
        self._draw_title(draw, title)
        self._draw_bottom_bar(draw, slide_number, total_slides)
        
        # === BULLET CARDS (max 4) ===
        bullets_to_show = bullets[:4]  # Limit to 4
        bullet_y = self.design.content_zone_start
        
        for bullet in bullets_to_show:
            self._draw_bullet_card(draw, bullet, self.design.margin_x, bullet_y)
            bullet_y += self.design.bullet_card_height_single + self.design.card_spacing
        
        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path, quality=95)
        logger.info(f"Slide saved to {output_path}")
        return output_path
    
    def _draw_top_bar(self, draw: ImageDraw.Draw, course_label: Optional[str]):
        """Draw top bar with logo and course label."""
        # Logo (left)
        if self.logo:
            # Resize logo to fit (80x80)
            logo_size = 80
            logo_resized = self.logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            # Note: Can't paste on ImageDraw, need to handle in main canvas
            # For now, use text-based logo
        
        # Text-based logo
        draw.text(
            (self.design.margin_x, self.design.top_bar_start),
            self.brand_name,
            font=self.logo_font,
            fill=self.design.accent_color
        )
        
        # Course label (right)
        if course_label:
            bbox = draw.textbbox((0, 0), course_label, font=self.label_font)
            text_width = bbox[2] - bbox[0]
            x = self.design.width - self.design.margin_x - text_width
            
            draw.text(
                (x, self.design.top_bar_start + 20),
                course_label,
                font=self.label_font,
                fill=self.design.label_color
            )
    
    def _draw_title(self, draw: ImageDraw.Draw, title: str):
        """Draw title in title zone."""
        # Wrap title (max 2 lines)
        content_width = self.design.card_width
        title_lines = self._wrap_text(title, self.title_font, content_width)[:2]
        
        y = self.design.title_zone_start
        for line in title_lines:
            draw.text(
                (self.design.margin_x, y),
                line,
                font=self.title_font,
                fill=self.design.title_color
            )
            y += int(self.design.title_font_size * self.design.title_line_height)
    
    def _draw_bottom_bar(self, draw: ImageDraw.Draw, slide_number: int, total_slides: int):
        """Draw bottom bar with progress indicator."""
        # Progress bar
        bar_y = self.design.bottom_bar_start + 20
        bar_height = 6
        bar_width = self.design.card_width
        progress_filled = int((slide_number / total_slides) * bar_width)
        
        # Background
        draw.rectangle(
            [(self.design.margin_x, bar_y), (self.design.margin_x + bar_width, bar_y + bar_height)],
            fill=(71, 85, 105)
        )
        
        # Filled
        draw.rectangle(
            [(self.design.margin_x, bar_y), (self.design.margin_x + progress_filled, bar_y + bar_height)],
            fill=self.design.accent_color
        )
        
        # Slide number
        slide_text = f"{slide_number}/{total_slides}"
        bbox = draw.textbbox((0, 0), slide_text, font=self.label_font)
        text_width = bbox[2] - bbox[0]
        x = (self.design.width - text_width) // 2
        
        draw.text(
            (x, bar_y + 20),
            slide_text,
            font=self.label_font,
            fill=self.design.label_color
        )
    
    def _draw_image_card(self, canvas: Image.Image, image_path: Path, x: int, y: int):
        """Draw image card with rounded corners."""
        # Load image
        img = Image.open(image_path).convert("RGB")
        
        # Resize to fit card inner area (872x712)
        # Center crop to square first
        img_w, img_h = img.size
        crop_size = min(img_w, img_h)
        left = (img_w - crop_size) // 2
        top = (img_h - crop_size) // 2
        img = img.crop((left, top, left + crop_size, top + crop_size))
        
        # Resize to fit inner area
        img = img.resize(
            (self.design.image_card_inner_width, self.design.image_card_inner_height),
            Image.Resampling.LANCZOS
        )
        
        # Create card with rounded corners
        card = Image.new("RGB", (self.design.card_width, self.design.image_card_height), self.design.card_bg_color)
        
        # Paste image with padding
        card.paste(img, (self.design.card_padding, self.design.card_padding))
        
        # Apply rounded corners
        card = self._apply_rounded_corners(card, self.design.image_card_corner_radius)
        
        # Paste onto canvas
        canvas.paste(card, (x, y))
    
    def _draw_bullet_card(self, draw: ImageDraw.Draw, bullet: str, x: int, y: int):
        """Draw bullet card with rounded corners."""
        # Draw card background
        card_rect = [
            (x, y),
            (x + self.design.card_width, y + self.design.bullet_card_height_single)
        ]
        draw.rounded_rectangle(
            card_rect,
            radius=self.design.card_corner_radius,
            fill=self.design.card_bg_color
        )
        
        # Draw bullet text (with padding)
        text_x = x + self.design.card_padding
        text_y = y + self.design.card_padding
        text_width = self.design.card_width - (2 * self.design.card_padding)
        
        # Wrap text (max 2 lines)
        lines = self._wrap_text(bullet, self.body_font, text_width)[:2]
        
        for line in lines:
            draw.text(
                (text_x, text_y),
                line,
                font=self.body_font,
                fill=self.design.body_color
            )
            text_y += int(self.design.body_font_size * self.design.body_line_height)
    
    def _apply_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        """Apply rounded corners to an image."""
        # Create mask
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
        
        # Apply mask
        output = Image.new('RGBA', img.size, (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        return output.convert('RGB')
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max width."""
        words = text.split()
        lines = []
        current_line = []
        
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines


def get_slide_composer(brand_name: str = "VINA", logo_path: Optional[Path] = None) -> SlideComposer:
    """
    Get a slide composer instance.
    
    Args:
        brand_name: Brand name for text logo
        logo_path: Optional path to logo image
    
    Returns:
        Configured SlideComposer
    """
    return SlideComposer(brand_name=brand_name, logo_path=logo_path)
