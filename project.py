import os
import csv

"""Создаем класс для работы с ценами продуктов"""


class PriceMachine:

    def __init__(self, catalog_path='', output_html='output.html'):
        self.catalog_path = catalog_path  # Путь к каталогу
        self.output_html = output_html  # Имя выходного HTML-файла
        self.data = []
        self.result = ''

    def load_prices(self):
        """Mетод для загрузки данных о ценах из файлов"""
        if not os.path.isdir(self.catalog_path):
            print("Указанный путь не является каталогом.")
            return

        try:
            for filename in os.listdir(self.catalog_path):
                if 'price' in filename.lower() and filename.endswith('.csv'):
                    with open(os.path.join(self.catalog_path, filename), mode='r', encoding='utf-8') as file:
                        reader = csv.reader(file)  # Создаем объект для чтения строк из CSV-файла
                        headers = next(reader)  # Читаем первую строку файла, которая содержит заголовки столбцов
                        """Вызываем внутренний метод _search_product_price_weight, который определяет индексы столбцов 
                        для продукта, цены и веса на основе заголовков"""
                        product_col, price_col, weight_col = self._search_product_price_weight(headers)
                        """Перебираем все оставшиеся строки в файле, излекаем значения из строк 
                        по полученным индексам столбцов из заголовков"""
                        for row in reader:
                            product = row[product_col] if product_col is not None else ''
                            price = float(row[price_col]) if price_col is not None and row[price_col] else 0.0
                            weight = float(row[weight_col]) if weight_col is not None and row[weight_col] else 1.0
                            price_per_kg = price / weight if weight > 0 else 0.0  # Вычисляем цену за килограмм
                            """Добавляем словарь с данными о продукте в список self.data"""
                            self.data.append({
                                'product': product,
                                'price': price,
                                'weight': weight,
                                'file': filename,
                                'price_per_kg': price_per_kg
                            })

        except FileNotFoundError:
            print(f"Файл '{filename}' не найден.")
        except csv.Error as e:
            print(f"Ошибка чтения CSV файла '{filename}': {e}")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def _search_product_price_weight(self, headers):
        """Метод для поиска индексов столбцов в заголовках"""
        product_col = None
        price_col = None
        weight_col = None
        """Определяем индексы, если есть ключевые слова в заголовках"""
        try:
            for index, header in enumerate(headers):
                header = header.lower()
                if header in ['товар', 'название', 'наименование', 'продукт']:
                    product_col = index
                elif header in ['розница', 'цена']:
                    price_col = index
                elif header in ['вес', 'масса', 'фасовка']:
                    weight_col = index

            if product_col is None or price_col is None:
                raise ValueError("Недостаточно данных в заголовках для определения важных колонок.")
        except Exception as e:
            print(f"Ошибка при поиске колонок: {e}")
        return product_col, price_col, weight_col

    def export_to_html(self, fname=None):
        """Метод для экспорта собранных данных в HTML файл"""
        if fname is None:
            fname = self.output_html

        result = '''<!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>'''

        for index, item in enumerate(sorted(self.data, key=lambda x: x['price_per_kg'])):
            result += f'''
        <tr>
            <td>{index + 1}</td>
            <td>{item['product']}</td>
            <td>{item['price']:.2f}</td>
            <td>{item['weight']:.2f}</td>
            <td>{item['file']}</td>
            <td>{item['price_per_kg']:.2f}</td>
        </tr>'''

        result += '''</table></body></html>'''

        try:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(result)
        except Exception as e:
            print(f"Ошибка при записи в файл {fname}: {e}")

    def find_text(self, text):
        """Метод для поиска товаров по названию"""
        results = []
        for item in self.data:
            if text.lower() in item['product'].lower():
                results.append(item)
        """Возвращаем отсортированные результаты по возрастающей цене за килограмм"""
        return sorted(results, key=lambda x: x['price_per_kg'])


def main():
    """Функция управления пользовательским интерфейсом программы"""
    try:
        catalog_path = input("Пожалуйста, введите путь к папке с прайс-листами: ")
        pm = PriceMachine(catalog_path=catalog_path)
        pm.load_prices()

        while True:
            search_text = input(
                "\nВведите фрагмент названия товара для поиска (или 'exit' для завершения): ").strip().lower()
            if search_text == 'exit':
                break

            results = pm.find_text(search_text)

            if results:
                print('\n'.join(
                    [f"{i + 1}. {result['product']} - Цена: {result['price']:.2f}, Вес: {result['weight']:.2f}, "
                     f"Файл: {result['file']}, Цена за кг.: {result['price_per_kg']:.2f}" for i, result in
                     enumerate(results)]))
            else:
                print("Товар не найден.")

        output_file = input("Хотите сохранить результаты в HTML? (Y/N): ").upper()
        if output_file == 'Y':
            html_filename = input("Укажите имя файла для сохранения: ")
            pm.export_to_html(html_filename)
            print(f"Результаты сохранены в файл {html_filename}")
        elif output_file == 'N':
            print("Работа завершена")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
