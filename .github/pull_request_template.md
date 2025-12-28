
# Descrição

Descreva brevemente o que este Pull Request faz e por que a mudança é necessária.

Link para issue relacionada (se houver):

---

# Tipo de mudança
- [ ] Bugfix
- [ ] Nova funcionalidade
- [ ] Refatoração
- [ ] Documentação
- [ ] Outra (descrever abaixo)

Descrição curta:

---

# Como testar / checklist de validação
- [ ] Rode os testes: `pytest -q`
- [ ] Verifique formatação: `black --check .`
- [ ] Cobertura (local): `pytest --cov=app --cov-report=term`
- [ ] Teste manual (se aplicável): descreva os passos para reproduzir

Passos para reproduzir / validar:
1. 
2. 
3. 

---

# Notas sobre CI
- O CI roda `black --check` e `pytest` com coleta de cobertura. Se a cobertura estiver abaixo do limite configurado no CI, a pipeline falhará.
- Se este PR adiciona/atualiza dependências, atualize `requirements.txt` ou `dev-requirements.txt` conforme apropriado.

---

# Checklist do PR
- [ ] Meu código segue as convenções do projeto
- [ ] Adicionei/atualizei testes quando aplicável
- [ ] Atualizei a documentação quando necessário
- [ ] Todos os checks do CI passam

---

# Observações
Use este espaço para informações extras, notas de migração, impacto em produção, etc.
