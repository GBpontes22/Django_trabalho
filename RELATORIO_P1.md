# Relatorio do P1 - Biblioteca / Acervo

## Features obrigatorias

Na Feature 1, a listagem principal pesquisa livros pelo titulo ou pelo nome do autor e filtra pela situacao dos exemplares, `Disponivel` ou `Emprestado`. Esses campos foram escolhidos porque representam as duas perguntas mais frequentes no atendimento de uma biblioteca: localizar rapidamente uma obra e saber se ela pode ser emprestada. A busca e o filtro podem ser usados separados ou combinados; sem essa funcionalidade, o usuario precisaria percorrer manualmente todo o acervo e ainda abrir outros registros para descobrir a disponibilidade.

Na Feature 2, o formulario de livros rejeita um ano de publicacao maior que o ano atual. Essa regra foi implementada no `LivroForm` com `clean_ano()`, leitura por `self.cleaned_data.get('ano')` e `forms.ValidationError`. Ela protege a consistencia historica do catalogo, pois uma obra nao pode ter sido publicada no futuro. Sem a validacao, dados impossiveis poderiam ser gravados e prejudicar pesquisas, relatorios e a confiabilidade do acervo.

## Evidencias tecnicas

- A view le `q` e `status` com `request.GET.get()`.
- A pesquisa textual usa `icontains` e `Q()` para combinar titulo e autor.
- O filtro de situacao usa contagens condicionais dos exemplares.
- O template preserva o termo pesquisado e usa `{% empty %}` quando nao ha resultados.
- O formulario mostra a mensagem da validacao junto ao campo `ano`.
- Os testes automatizados cobrem filtros isolados, filtros combinados e o bloqueio do ano futuro.
