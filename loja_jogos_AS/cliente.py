import xmlrpc.client

server = xmlrpc.client.ServerProxy("http://localhost:8000/")

print("=== JOGOS DISPONÍVEIS NO BANCO ===")
produtos = server.listar_produtos()
for p in produtos:
    print(f"ID: {p['id']} | {p['nome']} ({p['categoria']}) - R$ {p['preco']} | Estoque: {p['estoque']}")

print("\n=== REALIZANDO UMA VENDA ===")
carrinho = [
    {'id_produto': 1, 'quantidade': 1},
    {'id_produto': 2, 'quantidade': 2}
]

resultado = server.realizar_venda(1, carrinho)
print("Resultado:", resultado)
