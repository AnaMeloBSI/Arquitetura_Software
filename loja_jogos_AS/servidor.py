from xmlrpc.server import SimpleXMLRPCServer
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="user_rpc",
        password="userpassword",
        database="loja_jogos"
    )

def cadastrar_produto(nome, categoria, preco, estoque):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produto (nome, categoria, preco, estoque) VALUES (%s, %s, %s, %s)",
        (nome, categoria, preco, estoque)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return "Produto cadastrado com sucesso!"

def listar_produtos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produto")
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()
    return produtos

def realizar_venda(id_cliente, itens):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        valor_total = 0.0
        detalhes_itens = []

        for item in itens:
            cursor.execute("SELECT id, nome, preco, estoque FROM produto WHERE id = %s", (item['id_produto'],))
            prod = cursor.fetchone()

            if not prod:
                return f"Erro: Produto ID {item['id_produto']} não encontrado."
            if prod['estoque'] < item['quantidade']:
                return f"Erro: Estoque insuficiente para o produto '{prod['nome']}'."

            subtotal = float(prod['preco']) * item['quantidade']
            valor_total += subtotal
            detalhes_itens.append({
                'id_produto': prod['id'],
                'quantidade': item['quantidade'],
                'preco_unitario': float(prod['preco'])
            })

        cursor.execute(
            "INSERT INTO venda (id_cliente, valor_total) VALUES (%s, %s)",
            (id_cliente, valor_total)
        )
        id_venda = cursor.lastrowid

        for item in detalhes_itens:
            cursor.execute(
                "INSERT INTO itemvenda (id_venda, id_produto, quantidade, preco_unitario) VALUES (%s, %s, %s, %s)",
                (id_venda, item['id_produto'], item['quantidade'], item['preco_unitario'])
            )
            cursor.execute(
                "UPDATE produto SET estoque = estoque - %s WHERE id = %s",
                (item['quantidade'], item['id_produto'])
            )

        conn.commit()
        return f"Venda #{id_venda} realizada com sucesso! Valor Total: R$ {valor_total:.2f}"

    except Exception as e:
        conn.rollback()
        return f"Erro ao processar venda: {str(e)}"
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    print("Servidor RPC de Venda de Jogos rodando na porta 8000...")
    server.register_function(cadastrar_produto, "cadastrar_produto")
    server.register_function(listar_produtos, "listar_produtos")
    server.register_function(realizar_venda, "realizar_venda")
    server.serve_forever()
