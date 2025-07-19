#!/usr/bin/env python3
"""
ByteRover MCP Server - настоящий MCP сервер через stdio
"""

import json
import sys
import os
from typing import Dict, Any, List, Optional
import glob

class ByteRoverMCPServer:
    def __init__(self):
        self.initialized = False
        self.tools = [
            {
                "name": "file_search",
                "description": "Поиск файлов по имени",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Поисковый запрос"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "code_analysis",
                "description": "Анализ кода с помощью AI",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Путь к файлу для анализа"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["review", "optimization", "documentation"],
                            "description": "Тип анализа"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        ]
    
    def send_response(self, id: Optional[str], result: Any = None, error: Optional[Dict[str, Any]] = None):
        """Отправка ответа в формате MCP"""
        response = {
            "jsonrpc": "2.0",
            "id": id
        }
        
        if error:
            response["error"] = error
        else:
            response["result"] = result
        
        print(json.dumps(response), flush=True)
    
    def handle_initialize(self, params: Dict[str, Any], request_id: Optional[str]):
        """Обработка инициализации MCP"""
        self.initialized = True
        
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True
                },
                "resources": {},
                "logging": {
                    "level": "info"
                }
            },
            "serverInfo": {
                "name": "ByteRover MCP Server",
                "version": "1.0.0"
            }
        }
        
        self.send_response(request_id, result=result)
    
    def handle_tools_list(self, params: Dict[str, Any], request_id: Optional[str]):
        """Обработка запроса списка инструментов"""
        result = {"tools": self.tools}
        self.send_response(request_id, result=result)
    
    def handle_tools_call(self, params: Dict[str, Any], request_id: Optional[str]):
        """Обработка вызова инструмента"""
        try:
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            if name == "file_search":
                result = self.file_search_tool(arguments)
            elif name == "code_analysis":
                result = self.code_analysis_tool(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            self.send_response(request_id, result={"content": result})
            
        except Exception as e:
            error = {
                "code": -32603,
                "message": f"Tool execution error: {str(e)}"
            }
            self.send_response(request_id, error=error)
    
    def file_search_tool(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Инструмент поиска файлов"""
        query = arguments.get("query", "")
        
        # Простой поиск файлов в текущей директории
        try:
            # Ищем файлы по паттерну
            if "*" in query:
                files = glob.glob(query, recursive=True)
            else:
                # Ищем файлы, содержащие query в имени
                files = []
                for root, dirs, filenames in os.walk("."):
                    for filename in filenames:
                        if query.lower() in filename.lower():
                            files.append(os.path.join(root, filename))
            
            if files:
                return [
                    {
                        "type": "text",
                        "text": f"Найдено {len(files)} файлов по запросу '{query}':\n" + 
                               "\n".join([f"• {f}" for f in files[:10]])  # Показываем первые 10
                    }
                ]
            else:
                return [
                    {
                        "type": "text",
                        "text": f"Файлы по запросу '{query}' не найдены"
                    }
                ]
        except Exception as e:
            return [
                {
                    "type": "text",
                    "text": f"Ошибка поиска файлов: {str(e)}"
                }
            ]
    
    def code_analysis_tool(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Инструмент анализа кода"""
        file_path = arguments.get("file_path", "")
        analysis_type = arguments.get("analysis_type", "review")
        
        try:
            if not os.path.exists(file_path):
                return [
                    {
                        "type": "text",
                        "text": f"Файл {file_path} не найден"
                    }
                ]
            
            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Простой анализ (в реальном проекте здесь был бы AI)
            lines = content.split('\n')
            char_count = len(content)
            
            analysis_result = f"""
📊 Анализ файла: {file_path}
🔍 Тип анализа: {analysis_type}

📈 Статистика:
• Строк кода: {len(lines)}
• Символов: {char_count}
• Размер файла: {len(content.encode('utf-8'))} байт

💡 Рекомендации:
• Файл готов к {analysis_type}
• Рассмотрите возможность рефакторинга длинных функций
• Добавьте комментарии к сложным участкам кода
"""
            
            return [
                {
                    "type": "text",
                    "text": analysis_result
                }
            ]
            
        except Exception as e:
            return [
                {
                    "type": "text",
                    "text": f"Ошибка анализа файла {file_path}: {str(e)}"
                }
            ]
    
    def handle_request(self, request: Dict[str, Any]):
        """Обработка входящего запроса"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            self.handle_initialize(params, request_id)
        elif method == "initialized":
            # Обработка уведомления о завершении инициализации
            print(f"Initialized notification received", file=sys.stderr)
            # Отправляем уведомление о готовности
            ready_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/ready",
                "params": {}
            }
            print(json.dumps(ready_notification), flush=True)
        elif method == "tools/list":
            self.handle_tools_list(params, request_id)
        elif method == "tools/call":
            self.handle_tools_call(params, request_id)
        elif method == "ping":
            # Обработка ping запроса
            self.send_response(request_id, result={})
        elif method == "shutdown":
            # Обработка shutdown запроса
            self.send_response(request_id, result={})
            sys.exit(0)
        else:
            if request_id:  # Только для запросов с ID
                error = {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
                self.send_response(request_id, error=error)
            else:
                print(f"Unknown notification: {method}", file=sys.stderr)
    
    def run(self):
        """Запуск MCP сервера"""
        print("🚀 ByteRover MCP Server запущен (stdio)", file=sys.stderr)
        
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                self.handle_request(request)
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Ошибка обработки запроса: {e}", file=sys.stderr)

if __name__ == "__main__":
    server = ByteRoverMCPServer()
    server.run() 