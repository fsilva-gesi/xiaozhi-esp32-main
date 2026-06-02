# Guia de placa personalizada

Este guia mostra como customizar um novo inicializador de placa para o projeto de chatbot de voz Xiaozhi AI. O Xiaozhi AI suporta mais de 70 placas da série ESP32, e o código de inicialização de cada placa está em seu próprio diretório.

## Aviso importante

> **Atenção**: para placas personalizadas, se a configuração de IO for diferente da placa original, não substitua diretamente a configuração existente ao compilar o firmware. Você deve criar um novo tipo de placa ou distinguir com `name` e macros `sdkconfig` diferentes no `builds` de `config.json`. Use `python scripts/release.py [nome_do_diretorio_da_placa]` para compilar e empacotar o firmware.
>
> Se você sobrescrever a configuração original, sua firmware personalizada poderá ser substituída pelo firmware padrão da placa em futuras atualizações OTA, causando mau funcionamento do dispositivo. Cada placa tem uma identificação única e um canal de atualização correspondente; manter essa exclusividade é essencial.

## Estrutura de diretório

O diretório de cada placa geralmente inclui os arquivos abaixo:

- `xxx_board.cc` - código principal de inicialização da placa, implementando as funcionalidades específicas da placa
- `config.h` - configurações da placa, definindo o mapeamento de pinos e outras opções de hardware
- `config.json` - configuração de compilação, indicando o chip alvo e opções especiais de compilação
- `README.md` - documentação específica da placa

## Passos para customizar uma placa

### 1. Crie um novo diretório da placa

Primeiro, crie um diretório em `boards/` com o formato `[marca]-[tipo-de-placa]`, por exemplo `m5stack-tab5`:

```bash
mkdir main/boards/my-custom-board
```

### 2. Crie os arquivos de configuração

#### config.h

Defina todas as configurações de hardware em `config.h`, incluindo:

- taxa de amostragem de áudio e pinos I2S
- endereço do codec de áudio e pinos I2C
- pinos de botão e LED
- parâmetros e pinos do display

Exemplo de referência (do `lichuang-c3-dev`):

```c
#ifndef _BOARD_CONFIG_H_
#define _BOARD_CONFIG_H_

#include <driver/gpio.h>

// Configuração de áudio
#define AUDIO_INPUT_SAMPLE_RATE  24000
#define AUDIO_OUTPUT_SAMPLE_RATE 24000

#define AUDIO_I2S_GPIO_MCLK GPIO_NUM_10
#define AUDIO_I2S_GPIO_WS   GPIO_NUM_12
#define AUDIO_I2S_GPIO_BCLK GPIO_NUM_8
#define AUDIO_I2S_GPIO_DIN  GPIO_NUM_7
#define AUDIO_I2S_GPIO_DOUT GPIO_NUM_11

#define AUDIO_CODEC_PA_PIN       GPIO_NUM_13
#define AUDIO_CODEC_I2C_SDA_PIN  GPIO_NUM_0
#define AUDIO_CODEC_I2C_SCL_PIN  GPIO_NUM_1
#define AUDIO_CODEC_ES8311_ADDR  ES8311_CODEC_DEFAULT_ADDR

// Configuração de botão
#define BOOT_BUTTON_GPIO        GPIO_NUM_9

// Configuração do display
#define DISPLAY_SPI_SCK_PIN     GPIO_NUM_3
#define DISPLAY_SPI_MOSI_PIN    GPIO_NUM_5
#define DISPLAY_DC_PIN          GPIO_NUM_6
#define DISPLAY_SPI_CS_PIN      GPIO_NUM_4

#define DISPLAY_WIDTH   320
#define DISPLAY_HEIGHT  240
#define DISPLAY_MIRROR_X true
#define DISPLAY_MIRROR_Y false
#define DISPLAY_SWAP_XY true

#define DISPLAY_OFFSET_X  0
#define DISPLAY_OFFSET_Y  0

#define DISPLAY_BACKLIGHT_PIN GPIO_NUM_2
#define DISPLAY_BACKLIGHT_OUTPUT_INVERT true

#endif // _BOARD_CONFIG_H_
```

#### config.json

Defina as configurações de compilação em `config.json`; esse arquivo é usado pelo script `scripts/release.py` para automatizar o build:

```json
{
    "target": "esp32s3",  // Chip alvo: esp32, esp32s3, esp32c3, esp32c6, esp32p4, etc.
    "builds": [
        {
            "name": "my-custom-board",  // Nome da placa para geração do pacote de firmware
            "sdkconfig_append": [
                // Configuração especial de tamanho de Flash
                "CONFIG_ESPTOOLPY_FLASHSIZE_8MB=y",
                // Configuração especial de tabela de partições
                "CONFIG_PARTITION_TABLE_CUSTOM_FILENAME=\"partitions/v2/8m.csv\""
            ]
        }
    ]
}
```

**Descrição das opções:**
- `target`: chip alvo, deve corresponder ao hardware
- `name`: nome do pacote de firmware gerado, idealmente igual ao nome do diretório
- `sdkconfig_append`: opções sdkconfig adicionais que serão anexadas à configuração padrão

**Configurações comuns de `sdkconfig_append`:**
```json
// Tamanho de Flash
"CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y"   // Flash de 4MB
"CONFIG_ESPTOOLPY_FLASHSIZE_8MB=y"   // Flash de 8MB
"CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y"  // Flash de 16MB

// Tabela de partições
"CONFIG_PARTITION_TABLE_CUSTOM_FILENAME=\"partitions/v2/4m.csv\""  // Partição 4MB
"CONFIG_PARTITION_TABLE_CUSTOM_FILENAME=\"partitions/v2/8m.csv\""  // Partição 8MB
"CONFIG_PARTITION_TABLE_CUSTOM_FILENAME=\"partitions/v2/16m.csv\"" // Partição 16MB

// Configuração de idioma
"CONFIG_LANGUAGE_EN_US=y"  // Inglês
"CONFIG_LANGUAGE_ZH_CN=y"  // Chinês simplificado

// Configuração de wake word
"CONFIG_USE_DEVICE_AEC=y"          // Habilita AEC no dispositivo
"CONFIG_WAKE_WORD_DISABLED=y"      // Desabilita wake word
```

### 3. Escreva o código de inicialização da placa

Crie `my_custom_board.cc` e implemente toda a lógica de inicialização da placa.

Um exemplo básico de definição de classe inclui:

1. **Definição de classe**: herda de `WifiBoard` ou `Ml307Board`
2. **Funções de inicialização**: inicializa I2C, display, botões, IoT, etc.
3. **Sobrescrita de funções virtuais**: como `GetAudioCodec()`, `GetDisplay()`, `GetBacklight()`
4. **Registro da placa**: use o macro `DECLARE_BOARD`

```cpp
#include "wifi_board.h"
#include "codecs/es8311_audio_codec.h"
#include "display/lcd_display.h"
#include "application.h"
#include "button.h"
#include "config.h"
#include "mcp_server.h"

#include <esp_log.h>
#include <driver/i2c_master.h>
#include <driver/spi_common.h>

#define TAG "MyCustomBoard"

class MyCustomBoard : public WifiBoard {
private:
    i2c_master_bus_handle_t codec_i2c_bus_;
    Button boot_button_;
    LcdDisplay* display_;

    void InitializeI2c() {
        i2c_master_bus_config_t i2c_bus_cfg = {
            .i2c_port = I2C_NUM_0,
            .sda_io_num = AUDIO_CODEC_I2C_SDA_PIN,
            .scl_io_num = AUDIO_CODEC_I2C_SCL_PIN,
            .clk_source = I2C_CLK_SRC_DEFAULT,
            .glitch_ignore_cnt = 7,
            .intr_priority = 0,
            .trans_queue_depth = 0,
            .flags = {
                .enable_internal_pullup = 1,
            },
        };
        ESP_ERROR_CHECK(i2c_new_master_bus(&i2c_bus_cfg, &codec_i2c_bus_));
    }

    void InitializeSpi() {
        spi_bus_config_t buscfg = {};
        buscfg.mosi_io_num = DISPLAY_SPI_MOSI_PIN;
        buscfg.miso_io_num = GPIO_NUM_NC;
        buscfg.sclk_io_num = DISPLAY_SPI_SCK_PIN;
        buscfg.quadwp_io_num = GPIO_NUM_NC;
        buscfg.quadhd_io_num = GPIO_NUM_NC;
        buscfg.max_transfer_sz = DISPLAY_WIDTH * DISPLAY_HEIGHT * sizeof(uint16_t);
        ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO));
    }

    void InitializeButtons() {
        boot_button_.OnClick([this]() {
            auto& app = Application::GetInstance();
            if (app.GetDeviceState() == kDeviceStateStarting) {
                EnterWifiConfigMode();
                return;
            }
            app.ToggleChatState();
        });
    }

    void InitializeDisplay() {
        esp_lcd_panel_io_handle_t panel_io = nullptr;
        esp_lcd_panel_handle_t panel = nullptr;

        esp_lcd_panel_io_spi_config_t io_config = {};
        io_config.cs_gpio_num = DISPLAY_SPI_CS_PIN;
        io_config.dc_gpio_num = DISPLAY_DC_PIN;
        io_config.spi_mode = 2;
        io_config.pclk_hz = 80 * 1000 * 1000;
        io_config.trans_queue_depth = 10;
        io_config.lcd_cmd_bits = 8;
        io_config.lcd_param_bits = 8;
        ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi(SPI2_HOST, &io_config, &panel_io));

        esp_lcd_panel_dev_config_t panel_config = {};
        panel_config.reset_gpio_num = GPIO_NUM_NC;
        panel_config.rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB;
        panel_config.bits_per_pixel = 16;
        ESP_ERROR_CHECK(esp_lcd_new_panel_st7789(panel_io, &panel_config, &panel));

        esp_lcd_panel_reset(panel);
        esp_lcd_panel_init(panel);
        esp_lcd_panel_invert_color(panel, true);
        esp_lcd_panel_swap_xy(panel, DISPLAY_SWAP_XY);
        esp_lcd_panel_mirror(panel, DISPLAY_MIRROR_X, DISPLAY_MIRROR_Y);

        display_ = new SpiLcdDisplay(panel_io, panel,
                                    DISPLAY_WIDTH, DISPLAY_HEIGHT,
                                    DISPLAY_OFFSET_X, DISPLAY_OFFSET_Y,
                                    DISPLAY_MIRROR_X, DISPLAY_MIRROR_Y, DISPLAY_SWAP_XY);
    }

    // Inicializa ferramentas MCP
    void InitializeTools() {
        // Consulte a documentação do MCP
    }

public:
    // Construtor
    MyCustomBoard() : boot_button_(BOOT_BUTTON_GPIO) {
        InitializeI2c();
        InitializeSpi();
        InitializeDisplay();
        InitializeButtons();
        InitializeTools();
        GetBacklight()->SetBrightness(100);
    }

    // Retorna o codec de áudio
    virtual AudioCodec* GetAudioCodec() override {
        static Es8311AudioCodec audio_codec(
            codec_i2c_bus_, 
            I2C_NUM_0, 
            AUDIO_INPUT_SAMPLE_RATE, 
            AUDIO_OUTPUT_SAMPLE_RATE,
            AUDIO_I2S_GPIO_MCLK, 
            AUDIO_I2S_GPIO_BCLK, 
            AUDIO_I2S_GPIO_WS, 
            AUDIO_I2S_GPIO_DOUT, 
            AUDIO_I2S_GPIO_DIN,
            AUDIO_CODEC_PA_PIN, 
            AUDIO_CODEC_ES8311_ADDR);
        return &audio_codec;
    }

    // Retorna o display
    virtual Display* GetDisplay() override {
        return display_;
    }
    
    // Retorna o controle de backlight
    virtual Backlight* GetBacklight() override {
        static PwmBacklight backlight(DISPLAY_BACKLIGHT_PIN, DISPLAY_BACKLIGHT_OUTPUT_INVERT);
        return &backlight;
    }
};

// Registra a placa
DECLARE_BOARD(MyCustomBoard);
```

### 4. Adicione a configuração do sistema de build

#### Adicione a opção da placa em Kconfig.projbuild

Abra `main/Kconfig.projbuild` e adicione a nova opção dentro de `choice BOARD_TYPE`:

```kconfig
choice BOARD_TYPE
    prompt "Board Type"
    default BOARD_TYPE_BREAD_COMPACT_WIFI
    help
        Board type. Tipo de placa
    
    # ... outras opções de placa ...
    
    config BOARD_TYPE_MY_CUSTOM_BOARD
        bool "My Custom Board (Minha placa personalizada)"
        depends on IDF_TARGET_ESP32S3  # Ajuste para o seu chip alvo
endchoice
```

**Observações:**
- `BOARD_TYPE_MY_CUSTOM_BOARD` deve ser todo em maiúsculas e usando underscore
- `depends on` define o chip alvo (`IDF_TARGET_ESP32S3`, `IDF_TARGET_ESP32C3`, etc.)
- A descrição pode usar português ou inglês

#### Adicione a configuração em CMakeLists.txt

Abra `main/CMakeLists.txt` e adicione o bloco correspondente ao seu tipo de placa:

```cmake
# Adicione sua configuração no encadeamento elseif
elseif(CONFIG_BOARD_TYPE_MY_CUSTOM_BOARD)
    set(BOARD_TYPE "my-custom-board")  # Deve coincidir com o nome do diretório
    set(BUILTIN_TEXT_FONT font_puhui_basic_20_4)  # Escolha a fonte conforme o tamanho do display
    set(BUILTIN_ICON_FONT font_awesome_20_4)
    set(DEFAULT_EMOJI_COLLECTION twemoji_64)  # Opcional, se precisar de emojis
endif()
```

**Descrição das fontes e emojis:**

Escolha o tamanho da fonte de acordo com a resolução do display:
- Tela pequena (128x64 OLED): `font_puhui_basic_14_1` / `font_awesome_14_1`
- Tela média-pequena (240x240): `font_puhui_basic_16_4` / `font_awesome_16_4`
- Tela média (240x320): `font_puhui_basic_20_4` / `font_awesome_20_4`
- Tela grande (480x320+): `font_puhui_basic_30_4` / `font_awesome_30_4`

Opções de coleção de emojis:
- `twemoji_32` - emojis 32x32 (telas pequenas)
- `twemoji_64` - emojis 64x64 (telas grandes)

### 5. Configuração e compilação

#### Método 1: use idf.py manualmente

1. **Defina o chip alvo** (na primeira configuração ou ao trocar de chip):
   ```bash
   # Para ESP32-S3
   idf.py set-target esp32s3
   
   # Para ESP32-C3
   idf.py set-target esp32c3
   
   # Para ESP32
   idf.py set-target esp32
   ```

2. **Limpe a configuração antiga**:
   ```bash
   idf.py fullclean
   ```

3. **Abra o menu de configuração**:
   ```bash
   idf.py menuconfig
   ```
   
   No menu, navegue até: `Xiaozhi Assistant` -> `Board Type` e selecione sua placa personalizada.

4. **Compile e grave**:
   ```bash
   idf.py build
   idf.py flash monitor
   ```

#### Método 2: use o script release.py (recomendado)

Se seu diretório de placa contém `config.json`, use o script para automatizar a configuração e compilação:

```bash
python scripts/release.py my-custom-board
```

O script irá automaticamente:
- ler o `target` em `config.json` e definir o chip alvo
- aplicar as opções em `sdkconfig_append`
- compilar e empacotar o firmware

### 6. Crie o README.md

Descreva no `README.md` as características da placa, requisitos de hardware e os passos de compilação e gravação.


## Componentes comuns de placas

### 1. Display

O projeto suporta vários drivers de display, incluindo:
- ST7789 (SPI)
- ILI9341 (SPI)
- SH8601 (QSPI)
- entre outros

### 2. Codec de áudio

Codecs compatíveis incluem:
- ES8311 (mais comum)
- ES7210 (matriz de microfones)
- AW88298 (amplificador de potência)
- entre outros

### 3. Gestão de energia

Algumas placas usam chips de gerenciamento de energia:
- AXP2101
- outros PMICs disponíveis

### 4. Controle de dispositivos MCP

Você pode adicionar diversas ferramentas MCP para o AI controlar:
- Speaker (controle de alto-falante)
- Screen (ajuste de brilho do display)
- Battery (leitura de carga da bateria)
- Light (controle de luz)
- entre outros

## Hierarquia de classes de placa

- `Board` - classe base da placa
  - `WifiBoard` - placas com conexão Wi-Fi
  - `Ml307Board` - placas com módulo 4G
  - `DualNetworkBoard` - placas que suportam troca entre Wi-Fi e 4G

## Dicas de desenvolvimento

1. **Considere placas similares**: se sua nova placa for parecida com uma existente, use a implementação como referência
2. **Depure em etapas**: comece com recursos básicos (como display) antes de adicionar áudio
3. **Mapeamento de pinos**: verifique se todos os pinos estão corretos em `config.h`
4. **Compatibilidade de hardware**: confirme que todos os chips e drivers são compatíveis

## Problemas comuns

1. **Display não exibe corretamente**: verifique a configuração de SPI, espelhamento e inversão de cor
2. **Sem saída de áudio**: verifique as configurações de I2S, o pino de habilitação do PA e o endereço do codec
3. **Não conecta à rede**: verifique as credenciais de Wi-Fi e a configuração de rede
4. **Não se comunica com o servidor**: verifique a configuração de MQTT ou WebSocket

## Referências

- Documentação ESP-IDF: https://docs.espressif.com/projects/esp-idf/
- Documentação LVGL: https://docs.lvgl.io/
- Documentação ESP-SR: https://github.com/espressif/esp-sr 