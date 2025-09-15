import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QMenuBar, QAction, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt


class GPACalculatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('学分绩点计算器')
        self.grades_data = []
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # 创建菜单栏
        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu('文件')
        import_action = QAction('导入 CSV...', self)
        import_action.triggered.connect(self.import_csv)
        file_menu.addAction(import_action)
        main_layout.addWidget(self.menu_bar)

        # 设置表格来显示和输入数据
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['课程名称', '成绩 (0-100)', '学分', '绩点'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellChanged.connect(self.on_cell_changed)
        main_layout.addWidget(self.table)

        # 添加一行按钮用于添加和删除行
        control_layout = QGridLayout()
        add_row_btn = QPushButton('添加一行')
        add_row_btn.clicked.connect(self.addRow)
        control_layout.addWidget(add_row_btn, 0, 0)

        remove_row_btn = QPushButton('删除一行')
        remove_row_btn.clicked.connect(self.removeRow)
        control_layout.addWidget(remove_row_btn, 0, 1)

        main_layout.addLayout(control_layout)

        # 添加计算按钮
        self.calculate_btn = QPushButton('计算平均学分绩点')
        self.calculate_btn.clicked.connect(self.calculate_gpa)
        main_layout.addWidget(self.calculate_btn)

        # 显示结果的标签
        self.result_label = QLabel('平均学分绩点: ')
        self.result_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(self.result_label)

        self.setLayout(main_layout)

    def on_cell_changed(self, row, column):
        # 仅当成绩列被修改时才重新计算绩点
        if column == 1:
            item = self.table.item(row, column)
            if item and item.text():
                try:
                    score = float(item.text())
                    gpa = self.get_gpa_from_score(score)
                    self.table.setItem(row, 3, QTableWidgetItem(f'{gpa:.2f}'))
                except ValueError:
                    # 如果输入不是数字，则清除绩点列
                    self.table.setItem(row, 3, QTableWidgetItem(''))

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "导入 CSV 文件", "", "CSV Files (*.csv)")
        if file_path:
            try:
                df = pd.read_csv(file_path)

                # 假设CSV文件包含 '课程名称', '成绩', '学分'
                if not all(col in df.columns for col in ['课程名称', '成绩', '学分']):
                    QMessageBox.warning(self, "错误", "CSV文件缺少必要的列：'课程名称', '成绩', '学分'")
                    return

                self.table.setRowCount(df.shape[0])
                for row_idx, row_data in df.iterrows():
                    self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['课程名称'])))
                    self.table.setItem(row_idx, 1, QTableWidgetItem(str(row_data['成绩'])))
                    self.table.setItem(row_idx, 2, QTableWidgetItem(str(row_data['学分'])))

                    # 自动根据成绩计算绩点
                    try:
                        score = float(row_data['成绩'])
                        gpa = self.get_gpa_from_score(score)
                        self.table.setItem(row_idx, 3, QTableWidgetItem(f'{gpa:.2f}'))
                    except ValueError:
                        self.table.setItem(row_idx, 3, QTableWidgetItem(''))

            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入文件时发生错误: {e}")

    def addRow(self):
        rowPosition = self.table.rowCount()
        self.table.insertRow(rowPosition)

    def removeRow(self):
        if self.table.rowCount() > 0:
            self.table.removeRow(self.table.rowCount() - 1)

    def get_gpa_from_score(self, score):
        if 95 <= score <= 100:
            return 4.0
        elif 90 <= score < 95:
            return 3.6
        elif 85 <= score < 90:
            return 3.2
        elif 80 <= score < 85:
            return 2.8
        elif 75 <= score < 80:
            return 2.4
        elif 70 <= score < 75:
            return 2.0
        elif 65 <= score < 70:
            return 1.6
        elif 60 <= score < 65:
            return 1.2
        elif score == 60:
            return 1.0
        else:
            return 0.0

    def calculate_gpa(self):
        total_credit_gpa = 0
        total_credits = 0

        for row in range(self.table.rowCount()):
            try:
                score_item = self.table.item(row, 1)
                credit_item = self.table.item(row, 2)

                if score_item is None or credit_item is None:
                    continue

                score = float(score_item.text())
                credit = float(credit_item.text())

                if credit > 0:
                    gpa = self.get_gpa_from_score(score)
                    total_credit_gpa += gpa * credit
                    total_credits += credit
            except (ValueError, TypeError):
                continue

        if total_credits > 0:
            average_gpa = total_credit_gpa / total_credits
            self.result_label.setText(f"平均学分绩点: {average_gpa:.2f}")
        else:
            self.result_label.setText("平均学分绩点: 0.00")
            QMessageBox.warning(self, "错误", "学分总和不能为零！")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GPACalculatorApp()
    ex.show()
    sys.exit(app.exec_())