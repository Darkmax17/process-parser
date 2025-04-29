import subprocess
from collections import defaultdict
import datetime
import os


def get_processes_linux():
    """Получает список процессов в Linux с информацией о пользователе и памяти"""
    try:
        result = subprocess.run(['ps', 'axo', 'user:20,pid,comm,%mem'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = result.stdout.strip().split('\n')[1:]  # пропускаем заголовок
        processes = []

        for line in lines:
            parts = line.strip().split(None, 3)
            if len(parts) < 4:
                continue
            user, pid, name, mem_percent = parts
            try:
                memory_mb = float(mem_percent) * os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 1024 / 1024 / 100
            except Exception:
                memory_mb = 0.0

            processes.append({
                'name': name,
                'pid': pid,
                'user': user,
                'memory_mb': memory_mb
            })
        return processes

    except Exception as e:
        print(f"Ошибка при получении списка процессов: {e}")
        return []


def get_cpu_usage_linux():
    """Получает загрузку CPU в Linux"""
    try:
        result = subprocess.run(['top', '-bn1'], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.split('\n'):
            if 'Cpu(s):' in line:
                # Пример строки: "%Cpu(s):  7.6 us,  2.0 sy,  0.0 ni, 89.6 id, ..."
                cpu_idle = float(line.split(',')[3].split()[0])
                return 100 - cpu_idle
    except Exception as e:
        print(f"Ошибка при получении CPU: {e}")
    return 0.0


def generate_report(processes, cpu_usage):
    """Генерирует текст отчета"""
    if not processes:
        return ["Не удалось получить информацию о процессах"]

    users = set()
    user_process_count = defaultdict(int)
    total_memory = 0.0
    max_memory_process = ('', 0.0)

    for proc in processes:
        users.add(proc['user'])
        user_process_count[proc['user']] += 1
        total_memory += proc['memory_mb']

        if proc['memory_mb'] > max_memory_process[1]:
            max_memory_process = (proc['name'], proc['memory_mb'])

    report = [
        "Отчёт о состоянии системы (Linux):",
        f"Пользователи системы: {', '.join(sorted(users))}",
        f"Процессов запущено: {len(processes)}",
        "\nПользовательских процессов:"
    ]

    for user, count in sorted(user_process_count.items(), key=lambda x: x[1], reverse=True):
        report.append(f"{user}: {count}")

    report.extend([
        f"\nВсего памяти используется: {total_memory:.1f} MB",
        f"Всего CPU используется: {cpu_usage:.1f}%",
        f"Больше всего памяти использует: {max_memory_process[0][:20]}{'...' if len(max_memory_process[0]) > 20 else ''} ({max_memory_process[1]:.1f} MB)"
    ])

    return report


def save_report(report_lines):
    now = datetime.datetime.now()
    filename = now.strftime("%d-%m-%Y-%H-%M") + "-scan.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    return os.path.abspath(filename)


def main():
    processes = get_processes_linux()
    cpu_usage = get_cpu_usage_linux()
    report = generate_report(processes, cpu_usage)
    print('\n'.join(report))
    saved_path = save_report(report)
    print(f"\nОтчёт сохранён в файл: {saved_path}")

if __name__ == "__main__":
    main()
