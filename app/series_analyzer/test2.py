from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame
import pyqtgraph as pg
import numpy as np

def create_graph():
    # PyQtGraph 위젯 생성
    plot_widget = pg.PlotWidget()

    # 예시 데이터 생성
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # 그래프 그리기
    plot_widget.plot(x, y, pen='b')

    return plot_widget

def main():
    app = QApplication([])

    main_window = QMainWindow()
    main_window.setWindowTitle("PyQtGraph in QFrame")

    central_widget = QWidget()
    main_layout = QVBoxLayout()

    # QFrame 생성
    frame = QFrame()
    print(type(frame))
    frame.setFrameShape(QFrame.Shape.StyledPanel)

    # QFrame에 PyQtGraph 위젯 추가
    graph_widget = create_graph()
    frame_layout = QVBoxLayout()
    frame_layout.addWidget(graph_widget)
    frame.setLayout(frame_layout)

    main_layout.addWidget(frame)
    central_widget.setLayout(main_layout)
    main_window.setCentralWidget(central_widget)

    main_window.show()
    app.exec()

if __name__ == "__main__":
    main()
