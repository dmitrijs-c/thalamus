"""
Drawing QT version of the Gaussian patterns on the screen based on the grid of the concentric circles.
key F = full screen
keys 1,2,3 = draw white square with alpha 128, 255, or nothing
key B = toggle background color between black and white
"""
import sys
import numpy as np
import random
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QRadialGradient, QColor, QFont
from PyQt5.QtCore import QPointF, Qt

class Size:
    """Class to store screen dimensions in pixels."""
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Converter:
  """Class to handle unit conversions between pixels, degrees, and real-world dimensions."""  
  def __init__(self, screen_pixels: Size, screen_width_m: float, screen_distance_m: float):
    # Initialize the screen parameters
    self.screen_pixels = screen_pixels
    self.screen_width_m = screen_width_m
    self.screen_distance_m = screen_distance_m
    # Calculate the screen width in radians
    self.screen_width_rad = 2*np.arctan2(screen_width_m/2, screen_distance_m)
    # Calculate radians per pixel
    self.rad_per_pixel = self.screen_width_rad/screen_pixels.width
    # Calculate degrees per pixel
    self.deg_per_pixel = 180/np.pi*self.rad_per_pixel
    # Calculate meters per pixel
    self.m_per_pixel = screen_width_m/screen_pixels.width

  def deg_to_pixel_abs(self, *args):
    """Convert degrees to absolute pixel coordinates."""
    result = self.deg_to_pixel_rel(*args)
    # Coordinates are relative to the center of the screen, so add the screen center to get absolute coordinates
    if len(result) == 2:
      return result[0] + self.screen_pixels.width/2, result[1] + self.screen_pixels.height/2,
    else:
      return result[0] + self.screen_pixels.width/2

  def deg_to_pixel_rel(self, *args):
    """Convert degrees to relative pixel coordinates."""
    if len(args) == 1: # Handle single argument case
      if isinstance(args[0], (float, int)):
        return args[0]/self.deg_per_pixel
      else:
        x, y = args[0][0], args[0][1]
    else:
      x, y = args[0], args[1]
    return x/self.deg_per_pixel, y/self.deg_per_pixel

class GaussianDemo(QWidget):
    def __init__(self):
        global background_color_gauss
        super().__init__()
        self.setWindowTitle("Gaussian Visual Patterns")
        self.setGeometry(100, 100, 1920, 1080)  # Set window size
        self.screen_size = Size(1920, 1080)  # Screen resolution in pixels
        self.converter = Converter(self.screen_size, 0.5283, 0.57)  # Real-world dimensions of the screen LG 24GQ50B-B

        # Set initial background color to black
        self.background_color = QColor(0, 0, 0, 255)
        self.set_background_color(self.background_color.red())
        background_color_gauss = QColor(self.background_color.red(), self.background_color.red(), self.background_color.red(), 255)

        # Configuration variables
        self.num_circles = 7  # Number of concentric circles for positions
        self.circle_radii = np.linspace(0, self.screen_size.height, self.num_circles)  # Radii of circles
        self.circle_radii += self.screen_size.width / self.num_circles # a sum of screen width and height based steps
        self.circle_radii = self.circle_radii[self.circle_radii <= self.screen_size.height]
        self.circle_radii /= 2
        self.positions = self.generate_positions_on_circles()  # Generate target positions
        self.luminance_per = 100  # Luminance in percentage
        self.orientation = 0  # Orientation of Gaussian in degrees
        self.target_width_deg = 1  # Target width in degrees
        self.target_height_deg = 1  # Target height in degrees
        self.target_width_pix = self.converter.deg_to_pixel_rel(self.target_width_deg)  # Width in pixels
        self.target_height_pix = self.converter.deg_to_pixel_rel(self.target_height_deg)  # Height in pixels
        self.gaussian_gradient = self.create_gaussian_gradient(
            QPointF(0, 0), self.target_width_pix / 2, background_color_gauss, deviations=1, brightness=self.luminance_per/100*255
        )  # Create Gaussian gradient

        # State variable for drawing options
        self.drawing_option = 0  # 0: No square, 1: White square with alpha 128, 2: White square with alpha 255

    def set_background_color(self, intensity):
        """Set the background color of the window using grayscale intensity."""
        color = QColor(intensity, intensity, intensity, 255)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.update()  # Trigger a repaint

    def generate_positions_on_circles(self):
        """Generate target positions on concentric circles."""
        positions = [
            QPointF(
                self.width() / 2 + radius * np.cos(angle),
                self.height() / 2 + radius * np.sin(angle),
            )
            for radius in self.circle_radii[::2]
            for angle in np.linspace(0, 2 * np.pi, 12, endpoint=False)
        ]
        random.shuffle(positions)  # Shuffle positions to randomize their order
        return positions

    def drawText(self, painter, event):
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont('Arial', 20))
        painter.drawText(event.rect(), Qt.AlignCenter, "Hello, Qt!")

    def create_gaussian_gradient(self, center, radius, background_color_gauss, deviations=1, brightness=255):
        """Create a Gaussian radial gradient."""
        gradient = QRadialGradient(center, radius)
        resolution = 1000  # Number of gradient levels
        for i in range(resolution):
            # level = int(brightness * np.exp(-(deviations * i / resolution) ** 2 / 2)) # original
            level = int(background_color_gauss.red() + (brightness - background_color_gauss.red())*np.exp(-(deviations*i/resolution)**2/(2))) # version that makes Gaussian colors bound by background
            gradient.setColorAt(i / resolution, QColor(level, level, level))
        # gradient.setColorAt(1, background_color_gauss) # Qt.black) # original
        gradient.setColorAt(1, QColor(background_color_gauss.red(), background_color_gauss.green(), background_color_gauss.blue(), 255)) #Qt.GlobalColor.black
        return gradient

    def calculate_photodiode_intensities(self, background_intensity):
        """Calculate two equidistant grayscale intensities for the photodiode squares."""
        max_intensity = 255
        min_intensity = 0
        if background_intensity == min_intensity:
            intensity1 = background_intensity + 64
            intensity2 = background_intensity + 128
        elif background_intensity == max_intensity:
            intensity1 = background_intensity - 64
            intensity2 = background_intensity - 128
        else:
            distance = min(background_intensity - min_intensity, max_intensity - background_intensity)
            intensity1 = background_intensity - distance
            intensity2 = background_intensity - int(distance/8)
        return intensity1, intensity2

    def paintEvent(self, event):
        """Main drawing logic for the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(255, 255, 255))  # Set pen color to white
        photodiode_square = QColor(0, 0, 0, 255)  # Grayscale with alpha 128
        painter.fillRect(int(self.width() - 150), int(self.height() - 150), 150, 150, photodiode_square) # background small square bottom-right
        painter.fillRect(0, 0, 150, 150, photodiode_square) # background small square top-left
        self.drawText(painter, event)

        # Dynamically calculate the center of the window
        center_x = int(self.width() / 2)
        center_y = int(self.height() / 2)

        # Draw the concentric circles
        for radius in self.circle_radii:
            painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        # Draw the center cross (XY axes)
        painter.drawLine(center_x, 0, center_x, self.height())  # Vertical line
        painter.drawLine(0, center_y, self.width(), center_y)  # Horizontal line

        # Draw angled lines for 30° increments
        for angle in np.arange(0, 360, 30):
            x = int(center_x + self.circle_radii[-1] * np.cos(np.radians(angle)))
            y = int(center_y + self.circle_radii[-1] * np.sin(np.radians(angle)))
            painter.drawLine(center_x, center_y, x, y)

        # Update positions of Gaussian patterns dynamically
        dynamic_positions = [
            QPointF(
                center_x + radius * np.cos(angle),
                center_y + radius * np.sin(angle),
            )
            for radius in self.circle_radii
            for angle in np.linspace(0, 2 * np.pi, 12, endpoint=False)
        ]

        # Draw Gaussian patterns
        for position in dynamic_positions:  # "for position in self.positions[:10]" Render the first N positions
            self.draw_gaussian(painter, position)

        # Calculate photodiode intensities based on the current background intensity
        background_intensity = self.background_color.red()
        intensity1, intensity2 = self.calculate_photodiode_intensities(background_intensity)

        # Draw the square in the bottom right corner based on the current drawing option
        if self.drawing_option == 1:
            photodiode_square = QColor(255, 0, 0, 255)  # Grayscale with alpha 128
            painter.fillRect(int(self.width() - 100), int(self.height() - 100), 100, 100, photodiode_square)
            painter.fillRect(0, 0, 100, 100, photodiode_square)
        elif self.drawing_option == 2:
            photodiode_square = QColor(intensity2, intensity2, intensity2, 255)  # Grayscale with alpha 255
            painter.fillRect(int(self.width() - 100), int(self.height() - 100), 100, 100, photodiode_square)
            painter.fillRect(0, 0, 100, 100, photodiode_square)
        elif self.drawing_option == 3:
            photodiode_square = QColor(0, 0, 0, 255)  # Grayscale with alpha 255
            painter.fillRect(int(self.width() - 100), int(self.height() - 100), 100, 100, photodiode_square)
            painter.fillRect(0, 0, 100, 100, photodiode_square)
        elif self.drawing_option == 4:
            photodiode_square = QColor(255, 255, 255, 255)  # Grayscale with alpha 255
            painter.fillRect(int(self.width() - 100), int(self.height() - 100), 100, 100, photodiode_square)
            painter.fillRect(0, 0, 100, 100, photodiode_square)

        painter.end()

    def draw_gaussian(self, painter, position):
        """Draw a Gaussian pattern at the specified position."""
        painter.save()
        painter.translate(position)  # Move to the target position
        painter.rotate(self.orientation)  # Apply rotation to Gaussian
        # Scale the Gaussian for the target width and height
        painter.scale(1, self.target_height_pix / self.target_width_pix)
        # Convert dimensions to integers to match QPainter.fillRect requirements
        painter.fillRect(
            int(-self.target_width_pix / 2),  # Top-left x-coordinate
            int(-self.target_height_pix / 2),  # Top-left y-coordinate
            int(self.target_width_pix),  # Width of the rectangle
            int(self.target_height_pix),  # Height of the rectangle
            self.gaussian_gradient  # Apply Gaussian gradient
            )
        painter.restore()
    
    def keyPressEvent(self, event):
        """Handle key press events to toggle full-screen mode and drawing options."""
        if event.key() == Qt.Key_Escape:
            self.close()  # Close the application
        elif event.key() == Qt.Key_F:
            # Toggle full-screen mode
            if self.isFullScreen():
                self.showNormal()  # Exit full-screen mode
            else:
                self.showFullScreen()  # Enter full-screen mode
        elif event.key() == Qt.Key_1:
            self.drawing_option = 0  # Do not draw anything in the bottom right corner
            self.update()  # Trigger a repaint
        elif event.key() == Qt.Key_2:
            self.drawing_option = 1  # Draw a white square with alpha 128
            self.update()  # Trigger a repaint
        elif event.key() == Qt.Key_3:
            self.drawing_option = 2  # Draw a white square with alpha 255
            self.update()  # Trigger a repaint
        elif event.key() == Qt.Key_4:
            self.drawing_option = 3  # Draw a white square with alpha 255
            self.update()  # Trigger a repaint
        elif event.key() == Qt.Key_5:
            self.drawing_option = 4  # Draw a white square with alpha 255
            self.update()  # Trigger a repaint
        elif event.key() == Qt.Key_B:
            # Toggle background color between black, white, and grey using grayscale intensity
            if self.background_color == QColor(0, 0, 0, 255):
                self.background_color = QColor(255, 255, 255, 255)  # White
            elif self.background_color == QColor(255, 255, 255, 255):
                self.background_color = QColor(128, 128, 128, 255)  # Grey
            else:
                self.background_color = QColor(0, 0, 0, 255)  # Black
            background_color_gauss = QColor(self.background_color.red(), self.background_color.red(), self.background_color.red())
            self.gaussian_gradient = self.create_gaussian_gradient(
                QPointF(0, 0), self.target_width_pix / 2, background_color_gauss, deviations=1, brightness=self.luminance_per/100*255
                )  # Create Gaussian gradient
            self.set_background_color(self.background_color.red())  # Use the red component as the intensity


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = GaussianDemo()
    demo.show() # Show the window of some defined size rather than full-screen
    # demo.showFullScreen()  # Set the window to full-screen mode
    sys.exit(app.exec_())