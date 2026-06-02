# Guia de configuração para compilação

Este documento explica como configurar e compilar o firmware para **Movecall Moji2.0 (versão derivada Xiaozhi AI)**.

## 🛠 Requisitos do ambiente
*   **Versão do ESP-IDF**: v5.5
*   **Modelo do chip**: ESP32-C5

## 🔗 Informações de hardware open source
Este projeto é baseado no seguinte design de hardware open source:
*   **Plataforma open source Lichuang**: [https://oshwhub.com/movecall/moji2](https://oshwhub.com/movecall/moji2)

---

## 🚀 Etapas de compilação

### 1. Definir o alvo de compilação
Primeiro, defina o chip alvo do projeto como ESP32-C5:
```bash
idf.py set-target esp32c5
```

### 2. Configurar o modelo da placa
Execute o comando abaixo para abrir o menu de configuração e selecionar o tipo de placa:
```bash
idf.py menuconfig
```

**No menu, siga o caminho abaixo:**
> **Xiaozhi Assistant** -> **Board Type** -> **Movecall Moji2.0 小智AI衍生版**

*Dica: após configurar, pressione **S** para salvar, pressione Enter para confirmar e pressione **Q** para sair.*

### 3. Executar a compilação
Execute o comando abaixo para iniciar a construção do projeto:
```bash
idf.py build
```

---

## 🔧 Comandos úteis de manutenção

**Limpar o cache de compilação (recomendado ao encontrar erros):**
```bash
idf.py fullclean
```

**Gravar o firmware:**
```bash
idf.py flash
```

**Visualizar logs da serial:**
```bash
idf.py monitor
```