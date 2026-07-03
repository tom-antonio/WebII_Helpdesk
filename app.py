from flask import Flask, jsonify, render_template, request, redirect, url_for, session

from dao.database import create_chamado, get_usuario_by_nome, list_chamados, update_chamado_status

app = Flask(__name__)
app.secret_key = 'webii-helpdesk-secret-key'


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')

	nome = request.form.get('username', '').strip()
	senha = request.form.get('password', '').strip()
	usuario = get_usuario_by_nome(nome)

	if usuario and usuario.get('senha') == senha:
		session['usuario_id'] = usuario['id']
		session['usuario_nome'] = usuario['nome']
		return redirect(url_for('consulta'))

	return render_template('login.html', erro='Usuário ou senha inválidos.')


@app.route('/chamado')
def chamado():
	return render_template('chamado.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
	if request.method == 'GET':
		return render_template('chamado.html')

	cliente = request.form.get('cliente', '').strip()
	descricao = request.form.get('descricao', '').strip()
	prioridade = request.form.get('prioridade', '').strip()

	if not cliente or not descricao or not prioridade:
		return redirect(url_for('chamado'))

	create_chamado(cliente, descricao, prioridade)
	return redirect(url_for('index'))


@app.route('/consulta')
def consulta():
	if not session.get('usuario_id'):
		return redirect(url_for('login'))
	atendimento = list_chamados() or []
	return render_template('tecnico_chamado.html', atendimento=atendimento)


@app.route('/fila')
def fila():
	atendimento = list_chamados() or []
	return render_template('fila.html', atendimento=atendimento)


@app.route('/voltar')
def voltar():
	return redirect(url_for('index'))


@app.route('/api/chamados')
def api_chamados():
	return jsonify(list_chamados() or [])


@app.route('/chamados/<int:chamado_id>/atender', methods=['POST'])
def atender_chamado(chamado_id):
	update_chamado_status(chamado_id, 'Em atendimento', False)
	return redirect(url_for('consulta'))


@app.route('/chamados/<int:chamado_id>/concluir', methods=['POST'])
def concluir_chamado(chamado_id):
	update_chamado_status(chamado_id, 'Resolvido', True)
	return redirect(url_for('consulta'))


@app.route('/chamados/<int:chamado_id>/cancelar', methods=['POST'])
def cancelar_chamado(chamado_id):
	update_chamado_status(chamado_id, 'Cancelado', True)
	return redirect(url_for('consulta'))


if __name__ == '__main__':
	app.run(debug=True)
    
