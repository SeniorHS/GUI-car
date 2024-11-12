import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Información de Ocupación')

        # Variables para mantener el estado de ocupación en cada sección
        self.total_normal = 200
        self.ocupados_normal = 0
        self.ocupados_ejecutivo = 0
        self.ocupados_reservas = 0
        self.ocupados_discapacitados = 0
        self.ocupados_mecanica = 0
        self.ocupados_ambulancia = 0

        main_layout = QVBoxLayout()

        # Sección "Normal"
        self.normal_layout = self.create_section('Normal', self.ocupados_normal, self.total_normal, "background-color: #D5F5E3;")
        main_layout.addLayout(self.normal_layout)

        # Sección "Ejecutivo" con botones de incremento y decremento
        ejecutivo_layout = self.create_section_with_buttons('Ejecutivo', self.ocupados_ejecutivo, 14, "background-color: #FADBD8;", 'ejecutivo')
        main_layout.addLayout(ejecutivo_layout)

        # Sección "Otros" con múltiples categorías
        otros_layout = self.create_otros_section_with_buttons()
        main_layout.addLayout(otros_layout)

        # Añadimos una imagen
        self.add_image(main_layout)

        self.setLayout(main_layout)

    def create_section(self, title, ocupados, disponibles, bg_color):
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"font-size: 24px; font-weight: bold; {bg_color}")

        # Mostrar ocupados
        self.ocupados_normal_label = QLabel(f'Ocupados: {ocupados}/{disponibles}')
        self.ocupados_normal_label.setAlignment(Qt.AlignCenter)
        self.ocupados_normal_label.setStyleSheet("color: red; font-size: 18px;")

        # Mostrar disponibles
        self.disponibles_normal_label = QLabel(f'Disponibles: {disponibles - ocupados}')
        self.disponibles_normal_label.setAlignment(Qt.AlignCenter)
        self.disponibles_normal_label.setStyleSheet("color: green; font-size: 18px;")

        layout.addWidget(title_label)
        layout.addWidget(self.ocupados_normal_label)
        layout.addWidget(self.disponibles_normal_label)  # Añadir el label de disponibles

        return layout

    def create_section_with_buttons(self, title, ocupados, disponibles, bg_color, section):
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"font-size: 24px; font-weight: bold; {bg_color}")

        ocupados_label = QLabel(f'{ocupados}/{disponibles}')
        ocupados_label.setAlignment(Qt.AlignCenter)
        ocupados_label.setStyleSheet("color: red; font-size: 18px;")

        btn_layout = QHBoxLayout()
        btn_incr = QPushButton('+')
        btn_decr = QPushButton('-')

        btn_incr.clicked.connect(lambda: self.update_count(ocupados_label, 1, 0, disponibles, section))
        btn_decr.clicked.connect(lambda: self.update_count(ocupados_label, -1, 0, disponibles, section))

        btn_layout.addWidget(btn_decr)
        btn_layout.addWidget(btn_incr)

        layout.addWidget(title_label)
        layout.addWidget(ocupados_label)
        layout.addLayout(btn_layout)

        return layout

    def create_otros_section_with_buttons(self):
        layout = QGridLayout()
        layout.setSpacing(20)

        title_label = QLabel('Otros')
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; background-color: #E8DAEF;")
        layout.addWidget(title_label, 0, 0, 1, 4)

        headers = ["Reservas", "Discapacitados", "Mecánica", "Ambulancia"]
        colors = ["#F7DC6F", "#85C1E9", "#F1948A", "#D2B4DE"]
        max_values = [5, 7, 2, 1]
        sections = ["reservas", "discapacitados", "mecanica", "ambulancia"]

        for col, (header, color, max_val, section) in enumerate(zip(headers, colors, max_values, sections)):
            label = QLabel(header)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(f"background-color: {color}; font-size: 16px; font-weight: bold;")
            layout.addWidget(label, 1, col)

            value_label = QLabel(f'0/{max_val}')
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-size: 16px;")
            layout.addWidget(value_label, 2, col)

            btn_incr = QPushButton('+')
            btn_decr = QPushButton('-')

            btn_incr.clicked.connect(lambda _, lbl=value_label, max_val=max_val, sec=section: self.update_count(lbl, 1, 0, max_val, sec))
            btn_decr.clicked.connect(lambda _, lbl=value_label, max_val=max_val, sec=section: self.update_count(lbl, -1, 0, max_val, sec))

            btn_layout = QHBoxLayout()
            btn_layout.addWidget(btn_decr)
            btn_layout.addWidget(btn_incr)

            layout.addLayout(btn_layout, 3, col)

        return layout

    def update_count(self, label, change, min_val, max_val, section):
        current_count = int(label.text().split('/')[0])  # Obtener el valor actual
        new_count = current_count + change

        if min_val <= new_count <= max_val:
            label.setText(f"{new_count}/{max_val}")
            self.update_total(section, change)

    def update_total(self, section, change):
        # Actualizar el total de ocupados en la sección correspondiente
        if section == 'ejecutivo':
            self.ocupados_ejecutivo += change
        elif section == 'reservas':
            self.ocupados_reservas += change
        elif section == 'discapacitados':
            self.ocupados_discapacitados += change
        elif section == 'mecanica':
            self.ocupados_mecanica += change
        elif section == 'ambulancia':
            self.ocupados_ambulancia += change

        # Calcular el total ocupado en la sección "Normal"
        self.ocupados_normal = (
            self.ocupados_ejecutivo + self.ocupados_reservas +
            self.ocupados_discapacitados + self.ocupados_mecanica +
            self.ocupados_ambulancia
        )
        
        # Calcular disponibles
        disponibles_normal = self.total_normal - self.ocupados_normal
        
        # Actualizar el label de "Normal" en tiempo real
        self.ocupados_normal_label.setText(f'Ocupados: {self.ocupados_normal}/{self.total_normal}')
        # Actualizar el label de "Disponibles" en tiempo real
        self.disponibles_normal_label.setText(f'Disponibles: {disponibles_normal}')

    def add_image(self, layout):
        image_label = QLabel()
        pixmap = QPixmap("background.jpg")
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())
