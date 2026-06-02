# BluFi Provisionamento (integrado com esp-wifi-connect)

Este documento descreve como ativar e usar o BluFi (provisionamento BLE Wi‑Fi) no firmware Xiaozhi, em conjunto com o componente `esp-wifi-connect` do projeto para concluir a conexão e armazenamento de Wi‑Fi. Para detalhes do protocolo BluFi, consulte a documentação oficial da [Espressif](https://docs.espressif.com/projects/esp-idf/zh_CN/stable/esp32/api-guides/ble/blufi.html).

## Pré-requisitos

- É necessário um chip compatível com BLE e configuração de firmware adequada.
- No `idf.py menuconfig`, habilite `WiFi Configuration Method -> Esp Blufi` (`CONFIG_USE_ESP_BLUFI_WIFI_PROVISIONING=y`). Se quiser usar BluFi, deve desativar a opção Hotspot no mesmo menu, caso contrário o provisionamento por Hotspot será usado por padrão.
- Mantenha a inicialização padrão do NVS e do loop de eventos (o `app_main` do projeto já cuida disso).
- As macros `CONFIG_BT_BLUEDROID_ENABLED` e `CONFIG_BT_NIMBLE_ENABLED` devem ser escolhidas alternadamente; não habilite as duas ao mesmo tempo.

## Fluxo de trabalho

1) O app no celular se conecta ao dispositivo via BluFi (por exemplo, o app oficial EspBlufi ou um cliente próprio), envia o SSID/senha do Wi‑Fi e pode obter a lista de Wi‑Fis detectados pelo dispositivo via protocolo BluFi.
2) No dispositivo, as credenciais são gravadas no `SsidManager` em `ESP_BLUFI_EVENT_REQ_CONNECT_TO_AP` (armazenadas no NVS como parte do componente `esp-wifi-connect`).
3) Em seguida, o `WifiStation` é iniciado para escanear e conectar; o status é retornado via BluFi.
4) Se o provisionamento for bem-sucedido, o dispositivo se conecta automaticamente ao novo Wi‑Fi; se falhar, retorna um estado de erro.

## Passos de uso

1. Configuração: no menuconfig, habilite `Esp Blufi`. Compile e grave o firmware.
2. Acionar provisionamento: o dispositivo entra automaticamente no modo de provisionamento na primeira inicialização se não houver Wi‑Fi salvo.
3. No celular: abra o EspBlufi App (ou outro cliente BluFi), localize e conecte ao dispositivo, escolha se deseja criptografia, e siga as instruções para enviar o SSID/senha do Wi‑Fi.
4. Verifique o resultado:
    - Sucesso: o BluFi informa que a conexão foi bem-sucedida e o dispositivo se conecta ao Wi‑Fi.
    - Falha: o BluFi retorna estado de erro; tente reenviar ou verifique o roteador.

## Observações

- BluFi e provisionamento por hotspot não podem ser usados simultaneamente. Se o hotspot estiver ativado, o provisionamento por hotspot será usado por padrão. Mantenha apenas um método habilitado em menuconfig.
- Ao testar mais de uma vez, é recomendável apagar ou sobrescrever o SSID armazenado no namespace `wifi` para evitar interferência de configurações antigas.
- Se usar um cliente BluFi personalizado, siga o formato de quadro do protocolo oficial conforme o link da documentação.
- A documentação oficial inclui o link para download do app EspBlufi.
- Devido a mudanças na interface BluFi no IDF 5.5.2, o nome Bluetooth compilado na versão 5.5.2 é "Xiaozhi-Blufi", enquanto na versão 5.5.1 é "BLUFI_DEVICE".

