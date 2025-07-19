#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы ByteRover MCP Server
"""

import json
import subprocess
import sys
import os

def test_mcp_server():
    """Тестирование MCP сервера"""
    print("🧪 Тестирование ByteRover MCP Server")
    print("=" * 50)
    
    # Запускаем MCP сервер
    try:
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.stdin is None or process.stdout is None:
            print("❌ Не удалось запустить MCP сервер")
            return False
        
        # Тест 1: Инициализация
        print("1. Тестирование инициализации...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        init_response = json.loads(response)
        
        if "result" in init_response:
            print("✅ Инициализация успешна")
            print(f"   Сервер: {init_response['result']['serverInfo']['name']}")
        else:
            print("❌ Ошибка инициализации")
            return False
        
        # Тест 2: Список инструментов
        print("\n2. Тестирование списка инструментов...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        tools_response = json.loads(response)
        
        if "result" in tools_response:
            tools = tools_response["result"]["tools"]
            print(f"✅ Найдено {len(tools)} инструментов:")
            for tool in tools:
                print(f"   • {tool['name']}: {tool['description']}")
        else:
            print("❌ Ошибка получения списка инструментов")
            return False
        
        # Тест 3: Поиск файлов
        print("\n3. Тестирование поиска файлов...")
        file_search_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "file_search",
                "arguments": {
                    "query": "*.py"
                }
            }
        }
        
        process.stdin.write(json.dumps(file_search_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        search_response = json.loads(response)
        
        if "result" in search_response:
            print("✅ Поиск файлов работает")
            content = search_response["result"]["content"][0]["text"]
            print(f"   Результат: {content[:100]}...")
        else:
            print("❌ Ошибка поиска файлов")
            return False
        
        # Тест 4: Анализ кода
        print("\n4. Тестирование анализа кода...")
        analysis_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "code_analysis",
                "arguments": {
                    "file_path": "mcp_server.py",
                    "analysis_type": "review"
                }
            }
        }
        
        process.stdin.write(json.dumps(analysis_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        analysis_response = json.loads(response)
        
        if "result" in analysis_response:
            print("✅ Анализ кода работает")
            content = analysis_response["result"]["content"][0]["text"]
            print(f"   Результат: {content[:100]}...")
        else:
            print("❌ Ошибка анализа кода")
            return False
        
        # Завершаем процесс
        process.terminate()
        process.wait()
        
        print("\n" + "=" * 50)
        print("🎉 Все тесты прошли успешно!")
        print("MCP сервер готов к использованию в Cursor")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1) 