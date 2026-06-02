# Guia de estilo de código

## Ferramenta de formatação de código

Este projeto usa a ferramenta `clang-format` para unificar o estilo do código. Já fornecemos um arquivo `.clang-format` na raiz do projeto, baseado no guia de estilo Google C++ com alguns ajustes personalizados.

### Instalar clang-format

Antes de usar, certifique-se de que o `clang-format` está instalado:

- **Windows**：
  ```powershell
  winget install LLVM
  # ou use Chocolatey
  choco install llvm
  ```

- **Linux**：
  ```bash
  sudo apt install clang-format  # Ubuntu/Debian
  sudo dnf install clang-tools-extra  # Fedora
  ```

- **macOS**：
  ```bash
  brew install clang-format
  ```

### Como usar

1. **Formatar um único arquivo**：
   ```bash
   clang-format -i path/to/your/file.cpp
   ```

2. **Formatar todo o projeto**：
   ```bash
   # Execute na raiz do projeto
   find main -iname *.h -o -iname *.cc | xargs clang-format -i
   ```

3. **Verificar o formato antes de commitar**：
   ```bash
   # Verifica se o arquivo segue o padrão (sem modificar o arquivo)
   clang-format --dry-run -Werror path/to/your/file.cpp
   ```

### Integração com IDE

- **Visual Studio Code**：
  1. Instale a extensão C/C++
  2. Ative `C_Cpp.formatting` em `clang-format`
  3. Você pode habilitar formatação automática ao salvar: `editor.formatOnSave: true`

- **CLion**：
  1. Nas configurações, selecione `Editor > Code Style > C/C++`
  2. Ajuste `Formatter` para `clang-format`
  3. Escolha usar o arquivo `.clang-format` do projeto

### Regras principais de formatação

- Indentação com 4 espaços
- Largura máxima de linha de 100 caracteres
- Chaves no estilo Attach (na mesma linha da instrução de controle)
- Ponteiros e referências alinhados à esquerda
- Inclusões de headers ordenadas automaticamente
- Modificadores de acesso de classe com indentação de -4 espaços

### Observações

1. Antes de enviar o código, garanta que ele foi formatado.
2. Não ajuste manualmente o alinhamento de código já formatado.
3. Se quiser que um trecho não seja formatado, use estes comentários:
   ```cpp
   // clang-format off
   // seu código
   // clang-format on
   ```

### FAQ

1. **Formatação falhou**：
   - Verifique se a versão do `clang-format` não é muito antiga
   - Certifique-se de que o arquivo está em UTF-8
   - Valide se o arquivo `.clang-format` está sintaticamente correto

2. **O resultado não está de acordo com o esperado**：
   - Confira se está usando o `.clang-format` da raiz do projeto
   - Confirme se não há outro `.clang-format` sendo priorizado em outro local

Se tiver dúvidas ou sugestões, abra uma issue ou envie um pull request.