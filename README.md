## Примеры запуска

Программа поддерживает несколько способов указания пути к логам для обработки. Ниже приведены примеры запуска с различными типами входных данных:

### 1. Запуск (nginx логи):

```bash
PYTHONPATH=. python src/main.py --path src/data/mini_logs.txt
python src/main.py --path src/data/nginx_logs.txt
python src/main.py --path src/data/mini_logs.txt
python main.py --path https://raw.githubusercontent.com/elastic/examples/master/Common%20Data%20Formats/nginx_logs/nginx_logs
