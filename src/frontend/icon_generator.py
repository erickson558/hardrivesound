"""
Generador de iconos para la bandeja del sistema.
Crea iconos personalizables en diferentes estilos.
"""
from typing import Optional
from src.utils.logger import logger

try:
    from PIL import Image, ImageDraw
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.error("❌ PIL no disponible")


class IconGenerator:
    """Generador de iconos para la bandeja del sistema"""
    
    ICON_SIZE = (64, 64)
    
    def __init__(self, style: str = 'modern'):
        """
        Inicializar generador de iconos.
        
        Args:
            style: Estilo del icono (modern, classic, simple, retro)
        """
        self.style = style
        
        if not PILLOW_AVAILABLE:
            logger.error("❌ IconGenerator no puede funcionar sin PIL")
    
    def create_icon(self, color: str) -> Optional[Image.Image]:
        """
        Crear icono según estilo y color.
        
        Args:
            color: Color del icono (green, red, gray)
            
        Returns:
            Imagen del icono o None si falla
        """
        if not PILLOW_AVAILABLE:
            return None
        
        try:
            if self.style == 'modern':
                return self._create_modern_icon(color)
            elif self.style == 'classic':
                return self._create_classic_icon(color)
            elif self.style == 'simple':
                return self._create_simple_icon(color)
            elif self.style == 'retro':
                return self._create_retro_icon(color)
            else:
                return self._create_modern_icon(color)
        except Exception as e:
            logger.error(f"❌ Error creando icono {self.style}: {e}")
            return self._create_fallback_icon(color)
    
    def _create_modern_icon(self, color: str) -> Image.Image:
        """Crear icono estilo moderno"""
        width, height = self.ICON_SIZE
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Colores según estado
        if color == "green":
            fill_color = (76, 175, 80, 255)
            accent_color = (56, 142, 60, 255)
        elif color == "red":
            fill_color = (244, 67, 54, 255)
            accent_color = (198, 40, 40, 255)
        else:
            fill_color = (158, 158, 158, 255)
            accent_color = (97, 97, 97, 255)
        
        # Círculo principal
        dc.ellipse([6, 6, width-6, height-6], fill=fill_color, outline=accent_color, width=2)
        
        # Brillo
        dc.ellipse([10, 10, 22, 22], fill=(255, 255, 255, 60))
        dc.ellipse([30, 30, 34, 34], fill=(255, 255, 255, 200))
        
        # Líneas de datos
        for i in range(4):
            angle = i * 90
            start_angle = angle - 20
            end_angle = angle + 20
            dc.arc([15, 15, width-15, height-15], start_angle, end_angle,
                  fill=(255, 255, 255, 120), width=3)
        
        return image
    
    def _create_classic_icon(self, color: str) -> Image.Image:
        """Crear icono estilo clásico"""
        width, height = self.ICON_SIZE
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Colores según estado
        if color == "green":
            fill_color = (0, 150, 0, 255)
            plate_color = (0, 100, 0, 255)
        elif color == "red":
            fill_color = (200, 0, 0, 255)
            plate_color = (150, 0, 0, 255)
        else:
            fill_color = (100, 100, 100, 255)
            plate_color = (70, 70, 70, 255)
        
        # Disco principal
        dc.ellipse([4, 4, width-4, height-4], fill=fill_color, outline=(0, 0, 0, 255), width=3)
        
        # Platos del disco
        for i in range(3):
            size = 20 + i * 12
            pos = (width - size) // 2
            dc.ellipse([pos, pos, pos+size, pos+size], fill=plate_color, outline=(0, 0, 0, 255), width=1)
        
        # Brazo de lectura
        dc.rectangle([30, 15, 33, 35], fill=(200, 200, 200, 255))
        dc.ellipse([28, 35, 35, 42], fill=(150, 150, 150, 255))
        dc.rectangle([25, 12, 38, 15], fill=(50, 50, 50, 255))
        
        return image
    
    def _create_simple_icon(self, color: str) -> Image.Image:
        """Crear icono estilo simple"""
        width, height = self.ICON_SIZE
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Colores según estado
        if color == "green":
            fill_color = (0, 200, 0, 255)
        elif color == "red":
            fill_color = (255, 0, 0, 255)
        else:
            fill_color = (150, 150, 150, 255)
        
        # Círculo simple
        dc.ellipse([8, 8, width-8, height-8], fill=fill_color)
        dc.ellipse([30, 30, 34, 34], fill=(255, 255, 255, 200))
        
        return image
    
    def _create_retro_icon(self, color: str) -> Image.Image:
        """Crear icono estilo retro"""
        width, height = self.ICON_SIZE
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Colores según estado
        if color == "green":
            fill_color = (0, 255, 0, 255)
            glow_color = (0, 200, 0, 100)
        elif color == "red":
            fill_color = (255, 0, 0, 255)
            glow_color = (200, 0, 0, 100)
        else:
            fill_color = (128, 128, 128, 255)
            glow_color = (100, 100, 100, 100)
        
        # Efecto glow
        dc.ellipse([2, 2, width-2, height-2], fill=glow_color)
        dc.ellipse([6, 6, width-6, height-6], fill=fill_color, outline=(0, 0, 0, 255), width=2)
        
        # Líneas retro
        for i in range(8):
            x1 = 10 + i * 6
            y1 = 10
            x2 = 10
            y2 = 10 + i * 6
            dc.line([x1, y1, x2, y2], fill=(255, 255, 255, 80), width=1)
        
        # Texto HDD
        dc.text((20, 25), "HDD", fill=(0, 0, 0, 200))
        
        return image
    
    def _create_fallback_icon(self, color: str) -> Image.Image:
        """Crear icono de respaldo en caso de error"""
        rgb_color = {'green': 'green', 'red': 'red', 'gray': 'gray'}.get(color, 'gray')
        return Image.new('RGB', self.ICON_SIZE, rgb_color)
