# Guia de uso do MCP para controle IoT

> Este documento explica como implementar controle IoT em dispositivos ESP32 usando o protocolo MCP. Para detalhes do protocolo, consulte [`mcp-protocol_zh.md`](./mcp-protocol_zh.md).

## Introdução

MCP (Model Context Protocol) é um protocolo recomendado para controle IoT moderno. Ele usa o formato padrão JSON-RPC 2.0 para descobrir e invocar "ferramentas" (tools) entre o backend e o dispositivo, permitindo controle flexível.

## Fluxo de uso típico

1. O dispositivo se conecta ao backend via protocolo base (como WebSocket ou MQTT) após inicializar.
2. O backend chama `initialize` do MCP para iniciar a sessão.
3. O backend chama `tools/list` para obter todas as ferramentas suportadas pelo dispositivo e a descrição dos parâmetros.
4. O backend chama `tools/call` para invocar uma ferramenta específica e controlar o dispositivo.

Veja o formato e a interação do protocolo em [`mcp-protocol_zh.md`](./mcp-protocol_zh.md).

## Como registrar ferramentas no dispositivo

O dispositivo registra ferramentas chamando `McpServer::AddTool`, que torna a ferramenta acessível ao backend. A assinatura comum é:

```cpp
void AddTool(
    const std::string& name,           // Nome da ferramenta, deve ser único e organizado, como self.dog.forward
    const std::string& description,    // Descrição da ferramenta para o modelo entender a função
    const PropertyList& properties,    // Lista de parâmetros de entrada (pode estar vazia), tipos suportados: bool, integer, string
    std::function<ReturnValue(const PropertyList&)> callback // Implementação chamada quando a ferramenta é invocada
);
```
- `name`: identificador único, recomendado usar estilo "módulo.função".
- `description`: descrição em linguagem natural para ajudar o AI/usuário.
- `properties`: lista de parâmetros com tipos possíveis, intervalos e valores padrão.
- `callback`: lógica de execução quando o backend invoca a ferramenta; o retorno pode ser bool/int/string.

## Exemplo de registro típico (ESP-Hi)

```cpp
void InitializeTools() {
    auto& mcp_server = McpServer::GetInstance();
    // Exemplo 1: sem parâmetros, controla o movimento do robô para frente
    mcp_server.AddTool("self.dog.forward", "Move o robô para frente", PropertyList(), [this](const PropertyList&) -> ReturnValue {
        servo_dog_ctrl_send(DOG_STATE_FORWARD, NULL);
        return true;
    });
    // Exemplo 2: com parâmetros, define cor RGB do LED
    mcp_server.AddTool("self.light.set_rgb", "Define a cor RGB", PropertyList({
        Property("r", kPropertyTypeInteger, 0, 255),
        Property("g", kPropertyTypeInteger, 0, 255),
        Property("b", kPropertyTypeInteger, 0, 255)
    }), [this](const PropertyList& properties) -> ReturnValue {
        int r = properties["r"].value<int>();
        int g = properties["g"].value<int>();
        int b = properties["b"].value<int>();
        led_on_ = true;
        SetLedColor(r, g, b);
        return true;
    });
}
```

## Exemplos comuns de chamadas JSON-RPC

### 1. Obter lista de ferramentas
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": { "cursor": "" },
  "id": 1
}
```

### 2. Controlar deslocamento da base
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "self.chassis.go_forward",
    "arguments": {}
  },
  "id": 2
}
```

### 3. Alternar modo de iluminação
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "self.chassis.switch_light_mode",
    "arguments": { "light_mode": 3 }
  },
  "id": 3
}
```

### 4. Inverter câmera
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "self.camera.set_camera_flipped",
    "arguments": {}
  },
  "id": 4
}
```

## Observações
- Os nomes das ferramentas, parâmetros e retornos devem corresponder ao registro feito com `AddTool` no dispositivo.
- Recomenda-se usar MCP para controle IoT em novos projetos.
- Para o protocolo completo e usos avançados, consulte [`mcp-protocol_zh.md`](./mcp-protocol_zh.md). 