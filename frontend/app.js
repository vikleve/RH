/**
 * Sistema de Departamento Pessoal — Módulo 1: Cadastro de Colaboradores
 * Lógica do Frontend (Vanilla JavaScript)
 * Integração com API REST e fallback autônomo para LocalStorage
 */

// Estado global da aplicação
const Estado = {
  colaboradores: [],
  colaboradorEmEdicao: null,
  colaboradorParaInativar: null,
  filtros: {
    termo: '',
    situacao: 'ativo',
    setor: ''
  },
  usaApi: window.location.protocol.startsWith('http')
};

const API_BASE = '/api';

// ============================================================================
// Utilitários de Máscara e Validação
// ============================================================================
function normalizarCpf(cpf) {
  return String(cpf || '').replace(/\D/g, '');
}

function formatarCpf(cpf) {
  const d = normalizarCpf(cpf);
  if (d.length === 11) {
    return `${d.slice(0,3)}.${d.slice(3,6)}.${d.slice(6,9)}-${d.slice(9,11)}`;
  }
  return cpf;
}

function mascaraCpf(valor) {
  let v = normalizarCpf(valor).slice(0, 11);
  if (v.length > 9) return `${v.slice(0,3)}.${v.slice(3,6)}.${v.slice(6,9)}-${v.slice(9)}`;
  if (v.length > 6) return `${v.slice(0,3)}.${v.slice(3,6)}.${v.slice(6)}`;
  if (v.length > 3) return `${v.slice(0,3)}.${v.slice(3)}`;
  return v;
}

function mascaraTelefone(valor) {
  let v = String(valor || '').replace(/\D/g, '').slice(0, 11);
  if (v.length > 10) return `(${v.slice(0,2)}) ${v.slice(2,7)}-${v.slice(7)}`;
  if (v.length > 6) return `(${v.slice(0,2)}) ${v.slice(2,6)}-${v.slice(6)}`;
  if (v.length > 2) return `(${v.slice(0,2)}) ${v.slice(2)}`;
  return v;
}

function mascaraCep(valor) {
  let v = String(valor || '').replace(/\D/g, '').slice(0, 8);
  if (v.length > 5) return `${v.slice(0,5)}-${v.slice(5)}`;
  return v;
}

function formatarMoeda(valor) {
  const num = typeof valor === 'number' ? valor : parseFloat(String(valor).replace(/[^\d,-]/g, '').replace(',', '.')) || 0;
  return num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatarDataBR(dataIso) {
  if (!dataIso) return '--';
  const partes = String(dataIso).split('T')[0].split('-');
  if (partes.length === 3) {
    return `${partes[2]}/${partes[1]}/${partes[0]}`;
  }
  return dataIso;
}

function validarCpf(cpf) {
  const n = normalizarCpf(cpf);
  if (n.length !== 11) return false;
  if (/^(\d)\1{10}$/.test(n)) return false;

  let soma = 0;
  for (let i = 0; i < 9; i++) soma += parseInt(n[i], 10) * (10 - i);
  let resto = (soma * 10) % 11;
  let d1 = resto === 10 ? 0 : resto;
  if (d1 !== parseInt(n[9], 10)) return false;

  soma = 0;
  for (let i = 0; i < 10; i++) soma += parseInt(n[i], 10) * (11 - i);
  resto = (soma * 10) % 11;
  let d2 = resto === 10 ? 0 : resto;
  if (d2 !== parseInt(n[10], 10)) return false;

  return true;
}

function validarEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(email).trim());
}

// ============================================================================
// Notificações Toast
// ============================================================================
function exibirToast(mensagem, tipo = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${tipo}`;
  
  let icone = '✓';
  if (tipo === 'error') icone = '✕';
  if (tipo === 'warning') icone = '⚠';

  toast.innerHTML = `<strong>${icone}</strong> <span>${mensagem}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ============================================================================
// Camada de Dados (API e LocalStorage Fallback)
// ============================================================================
const DadosService = {
  async listar(filtros = {}) {
    if (Estado.usaApi) {
      try {
        const params = new URLSearchParams();
        if (filtros.termo) params.set('q', filtros.termo);
        if (filtros.situacao && filtros.situacao !== 'todos') params.set('situacao', filtros.situacao);
        if (filtros.setor) params.set('setor', filtros.setor);

        const resp = await fetch(`${API_BASE}/colaboradores?${params.toString()}`);
        const data = await resp.json();
        if (data.sucesso) return data.dados;
        throw new Error(data.mensagem || 'Erro ao carregar colaboradores.');
      } catch (e) {
        console.warn('API indisponível, utilizando armazenamento local:', e.message);
        Estado.usaApi = false;
      }
    }
    return this._listarLocal(filtros);
  },

  async obter(id) {
    if (Estado.usaApi) {
      try {
        const resp = await fetch(`${API_BASE}/colaboradores/${id}`);
        const data = await resp.json();
        if (data.sucesso) return data.dados;
        throw new Error(data.mensagem || 'Colaborador não encontrado.');
      } catch (e) {
        console.warn('Fallback para armazenamento local');
      }
    }
    return this._obterLocal(id);
  },

  async cadastrar(dados) {
    if (Estado.usaApi) {
      const resp = await fetch(`${API_BASE}/colaboradores`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
      });
      const data = await resp.json();
      if (!resp.ok) {
        const err = new Error(data.mensagem || 'Erro de validação');
        err.erros = data.erros;
        throw err;
      }
      return data.dados;
    }
    return this._cadastrarLocal(dados);
  },

  async atualizar(id, dados) {
    if (Estado.usaApi) {
      const resp = await fetch(`${API_BASE}/colaboradores/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
      });
      const data = await resp.json();
      if (!resp.ok) {
        const err = new Error(data.mensagem || 'Erro ao atualizar');
        err.erros = data.erros;
        throw err;
      }
      return data.dados;
    }
    return this._atualizarLocal(id, dados);
  },

  async inativar(id, motivo) {
    if (Estado.usaApi) {
      const resp = await fetch(`${API_BASE}/colaboradores/${id}/inativar`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ motivo, usuario: 'Administrador (RH/GTI)' })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.mensagem || 'Erro ao inativar colaborador');
      return data.dados;
    }
    return this._inativarLocal(id, motivo);
  },

  async reativar(id) {
    if (Estado.usaApi) {
      const resp = await fetch(`${API_BASE}/colaboradores/${id}/reativar`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ usuario: 'Administrador (RH/GTI)' })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.mensagem || 'Erro ao reativar colaborador');
      return data.dados;
    }
    return this._reativarLocal(id);
  },

  // Implementação Local (Fallback autônomo offline)
  _getStorage() {
    const raw = localStorage.getItem('DP_COLABORADORES');
    if (!raw) {
      const seed = [
        {
          id: 1,
          matricula: 'RH-1001',
          nome_completo: 'Mariana Ramos Ferreira',
          cpf: '529.982.247-25',
          rg: '33.444.555-6',
          data_nascimento: '1992-08-20',
          telefone: '(11) 98765-4321',
          email: 'mariana.ramos@empresa.com.br',
          logradouro: 'Av. Paulista',
          numero: '1000',
          bairro: 'Bela Vista',
          cidade: 'São Paulo',
          uf: 'SP',
          cep: '01310-100',
          data_admissao: '2021-05-10',
          cargo: 'Supervisora de DP',
          setor: 'Departamento Pessoal',
          salario_base: 5900.00,
          situacao: 'ativo',
          total_dependentes: 1,
          dependentes: [{ id: 1, nome: 'Julia Ferreira', cpf: '', parentesco: 'Filho(a)' }],
          historico: [
            {
              id: 1,
              data_hora: '2021-05-10 09:00:00',
              campo_alterado: 'Criação de Cadastro',
              valor_anterior: null,
              valor_novo: 'Colaborador admitido com matrícula RH-1001.',
              usuario_responsavel: 'Sistema/Administrador'
            }
          ]
        }
      ];
      localStorage.setItem('DP_COLABORADORES', JSON.stringify(seed));
      return seed;
    }
    return JSON.parse(raw);
  },

  _saveStorage(lista) {
    localStorage.setItem('DP_COLABORADORES', JSON.stringify(lista));
  },

  _listarLocal(filtros) {
    let lista = this._getStorage();
    if (filtros.situacao && filtros.situacao !== 'todos') {
      lista = lista.filter(c => c.situacao === filtros.situacao);
    }
    if (filtros.setor) {
      lista = lista.filter(c => c.setor === filtros.setor);
    }
    if (filtros.termo) {
      const t = filtros.termo.toLowerCase().trim();
      const cpfLimpo = normalizarCpf(t);
      lista = lista.filter(c => 
        c.nome_completo.toLowerCase().includes(t) ||
        c.matricula.toLowerCase().includes(t) ||
        c.cpf.includes(t) ||
        (cpfLimpo && normalizarCpf(c.cpf).includes(cpfLimpo))
      );
    }
    return lista;
  },

  _obterLocal(id) {
    const item = this._getStorage().find(c => c.id === parseInt(id, 10));
    if (!item) throw new Error('Colaborador não encontrado.');
    return item;
  },

  _cadastrarLocal(dados) {
    const lista = this._getStorage();
    const novoId = lista.length > 0 ? Math.max(...lista.map(c => c.id)) + 1 : 1;
    const agora = new Date().toISOString().replace('T', ' ').slice(0, 19);

    const novo = {
      ...dados,
      id: novoId,
      total_dependentes: (dados.dependentes || []).length,
      historico: [
        {
          id: 1,
          data_hora: agora,
          campo_alterado: 'Criação de Cadastro',
          valor_anterior: null,
          valor_novo: `Colaborador ${dados.nome_completo} cadastrado com matrícula ${dados.matricula}.`,
          usuario_responsavel: 'Administrador (RH/GTI)'
        }
      ]
    };
    lista.push(novo);
    this._saveStorage(lista);
    return novo;
  },

  _atualizarLocal(id, dados) {
    const lista = this._getStorage();
    const idx = lista.findIndex(c => c.id === parseInt(id, 10));
    if (idx === -1) throw new Error('Colaborador não encontrado');

    const antigo = lista[idx];
    const agora = new Date().toISOString().replace('T', ' ').slice(0, 19);
    const historico = antigo.historico || [];

    // Checar alterações
    if (antigo.cargo !== dados.cargo) {
      historico.unshift({ id: historico.length + 1, data_hora: agora, campo_alterado: 'Cargo', valor_anterior: antigo.cargo, valor_novo: dados.cargo, usuario_responsavel: 'Administrador (RH/GTI)' });
    }
    if (antigo.salario_base !== dados.salario_base) {
      historico.unshift({ id: historico.length + 1, data_hora: agora, campo_alterado: 'Salário-base', valor_anterior: formatarMoeda(antigo.salario_base), valor_novo: formatarMoeda(dados.salario_base), usuario_responsavel: 'Administrador (RH/GTI)' });
    }

    const atualizado = {
      ...antigo,
      ...dados,
      id: antigo.id,
      total_dependentes: (dados.dependentes || []).length,
      historico
    };
    lista[idx] = atualizado;
    this._saveStorage(lista);
    return atualizado;
  },

  _inativarLocal(id, motivo) {
    const lista = this._getStorage();
    const colab = lista.find(c => c.id === parseInt(id, 10));
    if (!colab) throw new Error('Colaborador não encontrado');
    const agora = new Date().toISOString().replace('T', ' ').slice(0, 19);
    colab.situacao = 'inativo';
    colab.historico = colab.historico || [];
    colab.historico.unshift({
      id: colab.historico.length + 1,
      data_hora: agora,
      campo_alterado: 'Situação do Vínculo',
      valor_anterior: 'ativo',
      valor_novo: `inativo (Motivo: ${motivo || 'Não informado'})`,
      usuario_responsavel: 'Administrador (RH/GTI)'
    });
    this._saveStorage(lista);
    return colab;
  },

  _reativarLocal(id) {
    const lista = this._getStorage();
    const colab = lista.find(c => c.id === parseInt(id, 10));
    if (!colab) throw new Error('Colaborador não encontrado');
    const agora = new Date().toISOString().replace('T', ' ').slice(0, 19);
    colab.situacao = 'ativo';
    colab.historico = colab.historico || [];
    colab.historico.unshift({
      id: colab.historico.length + 1,
      data_hora: agora,
      campo_alterado: 'Situação do Vínculo',
      valor_anterior: 'inativo',
      valor_novo: 'ativo',
      usuario_responsavel: 'Administrador (RH/GTI)'
    });
    this._saveStorage(lista);
    return colab;
  }
};

// ============================================================================
// Renderização e Controle da Interface
// ============================================================================
async function carregarColaboradores() {
  try {
    const lista = await DadosService.listar(Estado.filtros);
    Estado.colaboradores = lista;
    renderizarTabela(lista);
    atualizarMetricas();
  } catch (e) {
    exibirToast(e.message || 'Falha ao carregar colaboradores.', 'error');
  }
}

function renderizarTabela(lista) {
  const tbody = document.getElementById('corpo-tabela');
  const emptyState = document.getElementById('estado-vazio');
  tbody.innerHTML = '';

  if (!lista || lista.length === 0) {
    emptyState.classList.remove('hidden');
    return;
  }
  emptyState.classList.add('hidden');

  lista.forEach(colab => {
    const tr = document.createElement('tr');
    if (colab.situacao === 'inativo') tr.classList.add('row-inativo');

    const totalDep = colab.total_dependentes !== undefined ? colab.total_dependentes : (colab.dependentes ? colab.dependentes.length : 0);
    const badgeSituacao = colab.situacao === 'ativo' 
      ? '<span class="badge badge-ativo">Ativo</span>' 
      : '<span class="badge badge-inativo">Inativo</span>';

    const botaoStatus = colab.situacao === 'ativo'
      ? `<button class="btn-icon text-danger" title="Inativar Colaborador" onclick="abrirModalInativar(${colab.id})">
           <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line></svg>
         </button>`
      : `<button class="btn-icon text-success" title="Reativar Colaborador" onclick="reativarColaborador(${colab.id})">
           <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
         </button>`;

    tr.innerHTML = `
      <td><strong>${colab.matricula}</strong></td>
      <td>
        <div class="colab-cell-main">
          <span class="colab-name">${colab.nome_completo}</span>
          <span class="colab-sub">CPF: ${colab.cpf}</span>
        </div>
      </td>
      <td>
        <div class="colab-cell-main">
          <span>${colab.cargo}</span>
          <span class="colab-sub">${colab.setor}</span>
        </div>
      </td>
      <td><span class="text-money">${formatarMoeda(colab.salario_base)}</span></td>
      <td>
        <span class="badge badge-dep">${totalDep} dep.</span>
      </td>
      <td>${badgeSituacao}</td>
      <td class="text-right">
        <div class="table-actions">
          <button class="btn-icon" title="Ver Detalhes e Auditoria" onclick="abrirModalDetalhes(${colab.id})">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
          </button>
          <button class="btn-icon" title="Editar Cadastro" onclick="abrirModalEditar(${colab.id})">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
          </button>
          ${botaoStatus}
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

async function atualizarMetricas() {
  try {
    // Busca todos sem filtro para computar totais gerais
    const todos = await DadosService.listar({ situacao: 'todos' });
    const ativos = todos.filter(c => c.situacao === 'ativo').length;
    const inativos = todos.filter(c => c.situacao === 'inativo').length;
    const setores = new Set(todos.map(c => c.setor).filter(Boolean)).size;

    document.getElementById('stat-total').textContent = todos.length;
    document.getElementById('stat-ativos').textContent = ativos;
    document.getElementById('stat-inativos').textContent = inativos;
    document.getElementById('stat-setores').textContent = setores;
  } catch (e) {
    console.error('Erro ao atualizar métricas:', e);
  }
}

// ============================================================================
// Gerenciamento de Dependentes Dinâmicos no Formulário
// ============================================================================
function adicionarLinhaDependente(dados = {}) {
  const container = document.getElementById('container-dependentes');
  const emptyHint = document.getElementById('dependentes-vazio');
  emptyHint.classList.add('hidden');

  const row = document.createElement('div');
  row.className = 'dependente-row';
  row.innerHTML = `
    <div>
      <input type="text" class="form-control dep-nome" placeholder="Nome do Dependente *" value="${dados.nome || ''}" required>
    </div>
    <div>
      <input type="text" class="form-control dep-cpf" placeholder="CPF (Opcional)" maxlength="14" value="${dados.cpf || ''}">
    </div>
    <div>
      <select class="form-control select-control dep-parentesco" required>
        <option value="">Parentesco *</option>
        <option value="Filho(a)" ${dados.parentesco === 'Filho(a)' ? 'selected' : ''}>Filho(a)</option>
        <option value="Cônjuge/Companheiro(a)" ${dados.parentesco === 'Cônjuge/Companheiro(a)' ? 'selected' : ''}>Cônjuge/Companheiro(a)</option>
        <option value="Pai/Mãe" ${dados.parentesco === 'Pai/Mãe' ? 'selected' : ''}>Pai/Mãe</option>
        <option value="Enteado(a)" ${dados.parentesco === 'Enteado(a)' ? 'selected' : ''}>Enteado(a)</option>
        <option value="Irmão(ã)" ${dados.parentesco === 'Irmão(ã)' ? 'selected' : ''}>Irmão(ã)</option>
        <option value="Outro" ${dados.parentesco === 'Outro' ? 'selected' : ''}>Outro</option>
      </select>
    </div>
    <div>
      <button type="button" class="btn-icon text-danger btn-remover-dep" title="Remover Dependente">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
      </button>
    </div>
  `;

  // Máscara no CPF do dependente
  const cpfInput = row.querySelector('.dep-cpf');
  cpfInput.addEventListener('input', (e) => e.target.value = mascaraCpf(e.target.value));

  // Remoção
  row.querySelector('.btn-remover-dep').addEventListener('click', () => {
    row.remove();
    if (container.children.length === 0) emptyHint.classList.remove('hidden');
  });

  container.appendChild(row);
}

function coletarDependentesDoFormulario() {
  const rows = document.querySelectorAll('.dependente-row');
  const deps = [];
  rows.forEach(r => {
    const nome = r.querySelector('.dep-nome').value.trim();
    const cpf = r.querySelector('.dep-cpf').value.trim();
    const parentesco = r.querySelector('.dep-parentesco').value;
    if (nome || parentesco) {
      deps.push({ nome, cpf, parentesco });
    }
  });
  return deps;
}

// ============================================================================
// Modais: Formulário de Cadastro / Edição
// ============================================================================
function limparErrosFormulario() {
  document.querySelectorAll('.field-error').forEach(el => el.textContent = '');
  document.querySelectorAll('.form-control').forEach(el => el.classList.remove('is-invalid'));
  const alerta = document.getElementById('form-alerta-erro');
  alerta.classList.add('hidden');
  alerta.textContent = '';
}

function abrirModalNovo() {
  Estado.colaboradorEmEdicao = null;
  document.getElementById('form-modal-title').textContent = 'Cadastrar Novo Colaborador';
  document.getElementById('colaborador-id').value = '';
  document.getElementById('colaborador-form').reset();
  document.getElementById('campo-situacao').value = 'ativo';
  document.getElementById('container-dependentes').innerHTML = '';
  document.getElementById('dependentes-vazio').classList.remove('hidden');
  limparErrosFormulario();
  document.getElementById('modal-form').classList.remove('hidden');
}

async function abrirModalEditar(id) {
  try {
    const colab = await DadosService.obter(id);
    Estado.colaboradorEmEdicao = colab;
    document.getElementById('form-modal-title').textContent = `Editar Colaborador: ${colab.nome_completo}`;
    document.getElementById('colaborador-id').value = colab.id;

    // Preenchimento dos campos
    document.getElementById('campo-nome').value = colab.nome_completo || '';
    document.getElementById('campo-cpf').value = colab.cpf || '';
    document.getElementById('campo-rg').value = colab.rg || '';
    document.getElementById('campo-data-nasc').value = colab.data_nascimento || '';
    document.getElementById('campo-email').value = colab.email || '';
    document.getElementById('campo-telefone').value = colab.telefone || '';
    document.getElementById('campo-logradouro').value = colab.logradouro || '';
    document.getElementById('campo-numero').value = colab.numero || '';
    document.getElementById('campo-bairro').value = colab.bairro || '';
    document.getElementById('campo-cidade').value = colab.cidade || '';
    document.getElementById('campo-uf').value = colab.uf || '';
    document.getElementById('campo-cep').value = colab.cep || '';
    document.getElementById('campo-matricula').value = colab.matricula || '';
    document.getElementById('campo-data-adm').value = colab.data_admissao || '';
    document.getElementById('campo-situacao').value = colab.situacao || 'ativo';
    document.getElementById('campo-cargo').value = colab.cargo || '';
    document.getElementById('campo-setor').value = colab.setor || '';
    document.getElementById('campo-salario').value = formatarMoeda(colab.salario_base);

    // Dependentes
    const container = document.getElementById('container-dependentes');
    container.innerHTML = '';
    const deps = colab.dependentes || [];
    if (deps.length > 0) {
      document.getElementById('dependentes-vazio').classList.add('hidden');
      deps.forEach(d => adicionarLinhaDependente(d));
    } else {
      document.getElementById('dependentes-vazio').classList.remove('hidden');
    }

    limparErrosFormulario();
    document.getElementById('modal-form').classList.remove('hidden');
  } catch (e) {
    exibirToast(e.message || 'Erro ao carregar dados para edição.', 'error');
  }
}

function fecharModalForm() {
  document.getElementById('modal-form').classList.add('hidden');
  Estado.colaboradorEmEdicao = null;
}

// Submissão do Formulário
async function salvarColaborador(e) {
  e.preventDefault();
  limparErrosFormulario();

  const id = document.getElementById('colaborador-id').value;
  const isEdicao = Boolean(id);

  const dados = {
    nome_completo: document.getElementById('campo-nome').value.trim(),
    cpf: document.getElementById('campo-cpf').value.trim(),
    rg: document.getElementById('campo-rg').value.trim(),
    data_nascimento: document.getElementById('campo-data-nasc').value,
    email: document.getElementById('campo-email').value.trim(),
    telefone: document.getElementById('campo-telefone').value.trim(),
    logradouro: document.getElementById('campo-logradouro').value.trim(),
    numero: document.getElementById('campo-numero').value.trim(),
    bairro: document.getElementById('campo-bairro').value.trim(),
    cidade: document.getElementById('campo-cidade').value.trim(),
    uf: document.getElementById('campo-uf').value.trim().toUpperCase(),
    cep: document.getElementById('campo-cep').value.trim(),
    matricula: document.getElementById('campo-matricula').value.trim(),
    data_admissao: document.getElementById('campo-data-adm').value,
    situacao: document.getElementById('campo-situacao').value,
    cargo: document.getElementById('campo-cargo').value.trim(),
    setor: document.getElementById('campo-setor').value,
    salario_base: document.getElementById('campo-salario').value,
    dependentes: coletarDependentesDoFormulario()
  };

  // Pré-validação rápida no cliente
  const erros = {};
  if (!dados.nome_completo) erros.nome_completo = 'Nome completo é obrigatório.';
  if (!dados.cpf) erros.cpf = 'CPF é obrigatório.';
  else if (!validarCpf(dados.cpf)) erros.cpf = 'CPF inválido. Verifique os dígitos.';
  if (!dados.data_nascimento) erros.data_nascimento = 'Data de nascimento é obrigatória.';
  if (!dados.email) erros.email = 'E-mail é obrigatório.';
  else if (!validarEmail(dados.email)) erros.email = 'Formato de e-mail inválido.';
  if (!dados.matricula) erros.matricula = 'Matrícula é obrigatória.';
  if (!dados.data_admissao) erros.data_admissao = 'Data de admissão é obrigatória.';
  if (!dados.cargo) erros.cargo = 'Cargo é obrigatório.';
  if (!dados.setor) erros.setor = 'Setor é obrigatório.';
  if (!dados.salario_base) erros.salario_base = 'Salário-base é obrigatório.';

  if (Object.keys(erros).length > 0) {
    aplicarErrosNosCampos(erros);
    return;
  }

  try {
    if (isEdicao) {
      await DadosService.atualizar(id, dados);
      exibirToast('Colaborador atualizado com sucesso e alterações auditadas!', 'success');
    } else {
      await DadosService.cadastrar(dados);
      exibirToast('Novo colaborador cadastrado com sucesso!', 'success');
    }
    fecharModalForm();
    await carregarColaboradores();
  } catch (err) {
    if (err.erros) {
      aplicarErrosNosCampos(err.erros);
    } else {
      const alerta = document.getElementById('form-alerta-erro');
      alerta.textContent = err.message || 'Erro ao processar solicitação.';
      alerta.classList.remove('hidden');
    }
  }
}

function aplicarErrosNosCampos(erros) {
  let primeiroInvalido = null;
  for (const [campo, msg] of Object.entries(erros)) {
    const span = document.getElementById(`erro-${campo}`);
    if (span) span.textContent = Array.isArray(msg) ? msg.join(', ') : msg;

    const input = document.getElementById(`campo-${campo.replace('_', '-')}`) || 
                  document.querySelector(`[name="${campo}"]`);
    if (input) {
      input.classList.add('is-invalid');
      if (!primeiroInvalido) primeiroInvalido = input;
    }
  }
  if (primeiroInvalido) primeiroInvalido.focus();
}

// ============================================================================
// Modal: Visualização Completa de Detalhes e Histórico
// ============================================================================
async function abrirModalDetalhes(id) {
  try {
    const colab = await DadosService.obter(id);
    document.getElementById('detalhes-nome').textContent = colab.nome_completo;
    document.getElementById('detalhes-matricula-sub').textContent = `Matrícula: ${colab.matricula} • Situação: ${colab.situacao.toUpperCase()}`;

    // Ficha Cadastral
    document.getElementById('view-nome').textContent = colab.nome_completo;
    document.getElementById('view-cpf').textContent = colab.cpf;
    document.getElementById('view-rg').textContent = colab.rg || 'Não informado';
    document.getElementById('view-nasc').textContent = formatarDataBR(colab.data_nascimento);

    document.getElementById('view-email').textContent = colab.email;
    document.getElementById('view-telefone').textContent = colab.telefone || 'Não informado';
    const end = [colab.logradouro, colab.numero, colab.bairro, colab.cidade, colab.uf, colab.cep].filter(Boolean).join(', ');
    document.getElementById('view-endereco').textContent = end || 'Não informado';

    document.getElementById('view-matricula').textContent = colab.matricula;
    document.getElementById('view-admissao').textContent = formatarDataBR(colab.data_admissao);
    document.getElementById('view-cargo').textContent = colab.cargo;
    document.getElementById('view-setor').textContent = colab.setor;
    document.getElementById('view-salario').textContent = formatarMoeda(colab.salario_base);
    document.getElementById('view-situacao').innerHTML = colab.situacao === 'ativo' 
      ? '<span class="badge badge-ativo">Ativo</span>' 
      : '<span class="badge badge-inativo">Inativo</span>';

    // Dependentes
    const listaDep = colab.dependentes || [];
    document.getElementById('detalhes-qtd-dep').textContent = listaDep.length;
    const containerDep = document.getElementById('detalhes-lista-dependentes');
    if (listaDep.length === 0) {
      containerDep.innerHTML = '<p class="text-muted" style="padding:1rem;">Nenhum dependente cadastrado para este colaborador.</p>';
    } else {
      containerDep.innerHTML = `
        <table class="data-table">
          <thead>
            <tr><th>Nome do Dependente</th><th>CPF</th><th>Parentesco</th></tr>
          </thead>
          <tbody>
            ${listaDep.map(d => `
              <tr>
                <td><strong>${d.nome}</strong></td>
                <td>${d.cpf || 'Não informado'}</td>
                <td><span class="badge badge-dep">${d.parentesco}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }

    // Histórico de Alterações / Auditoria
    const timeline = document.getElementById('detalhes-timeline');
    const historico = colab.historico || [];
    if (historico.length === 0) {
      timeline.innerHTML = '<p class="text-muted">Nenhuma alteração registrada até o momento.</p>';
    } else {
      timeline.innerHTML = historico.map(h => {
        let detalheAlteracao = '';
        if (h.valor_anterior !== null && h.valor_anterior !== undefined && h.valor_anterior !== '') {
          detalheAlteracao = `De: <s>${h.valor_anterior}</s> &rarr; Para: <strong>${h.valor_novo}</strong>`;
        } else {
          detalheAlteracao = `<strong>${h.valor_novo}</strong>`;
        }

        return `
          <div class="timeline-item">
            <div class="timeline-header">
              <span class="timeline-action">${h.campo_alterado}</span>
              <span class="timeline-date">${h.data_hora}</span>
            </div>
            <div class="timeline-body">
              ${detalheAlteracao}
              <div class="timeline-user">Registrado por: ${h.usuario_responsavel || 'Sistema'}</div>
            </div>
          </div>
        `;
      }).join('');
    }

    // Botão de editar a partir do modal de detalhes
    document.getElementById('btn-editar-a-partir-detalhes').onclick = () => {
      fecharModalDetalhes();
      abrirModalEditar(colab.id);
    };

    document.getElementById('modal-detalhes').classList.remove('hidden');
  } catch (e) {
    exibirToast(e.message || 'Erro ao carregar detalhes.', 'error');
  }
}

function fecharModalDetalhes() {
  document.getElementById('modal-detalhes').classList.add('hidden');
}

// ============================================================================
// Modal: Inativação e Reativação Lógica
// ============================================================================
function abrirModalInativar(id) {
  const colab = Estado.colaboradores.find(c => c.id === id);
  if (!colab) return;

  Estado.colaboradorParaInativar = colab;
  document.getElementById('inativar-info-colaborador').innerHTML = `
    <strong>${colab.nome_completo}</strong> (Matrícula: ${colab.matricula})<br>
    Cargo: ${colab.cargo} • Setor: ${colab.setor}
  `;
  document.getElementById('inativar-motivo').value = '';
  document.getElementById('modal-inativar').classList.remove('hidden');
}

function fecharModalInativar() {
  document.getElementById('modal-inativar').classList.add('hidden');
  Estado.colaboradorParaInativar = null;
}

async function confirmarInativacao() {
  if (!Estado.colaboradorParaInativar) return;
  const id = Estado.colaboradorParaInativar.id;
  const motivo = document.getElementById('inativar-motivo').value.trim();

  try {
    await DadosService.inativar(id, motivo);
    exibirToast('Colaborador inativado com sucesso. Histórico preservado!', 'warning');
    fecharModalInativar();
    await carregarColaboradores();
  } catch (e) {
    exibirToast(e.message || 'Erro ao inativar colaborador.', 'error');
  }
}

async function reativarColaborador(id) {
  if (!confirm('Deseja reativar o vínculo deste colaborador?')) return;
  try {
    await DadosService.reativar(id);
    exibirToast('Colaborador reativado com sucesso!', 'success');
    await carregarColaboradores();
  } catch (e) {
    exibirToast(e.message || 'Erro ao reativar colaborador.', 'error');
  }
}

// ============================================================================
// Configuração de Eventos
// ============================================================================
function configurarEventos() {
  // Novo Colaborador
  document.getElementById('btn-novo-colaborador').addEventListener('click', abrirModalNovo);
  document.getElementById('btn-fechar-form-modal').addEventListener('click', fecharModalForm);
  document.getElementById('btn-cancelar-form').addEventListener('click', fecharModalForm);
  document.getElementById('colaborador-form').addEventListener('submit', salvarColaborador);

  // Dependentes
  document.getElementById('btn-adicionar-dependente').addEventListener('click', () => adicionarLinhaDependente());

  // Modal Detalhes
  document.getElementById('btn-fechar-detalhes').addEventListener('click', fecharModalDetalhes);
  document.getElementById('btn-fechar-detalhes-footer').addEventListener('click', fecharModalDetalhes);

  // Abas do Modal Detalhes
  document.querySelectorAll('.modal-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
      document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      e.currentTarget.classList.add('active');
      const targetId = e.currentTarget.getAttribute('data-tab');
      document.getElementById(targetId).classList.add('active');
    });
  });

  // Modal Inativar
  document.getElementById('btn-fechar-inativar').addEventListener('click', fecharModalInativar);
  document.getElementById('btn-cancelar-inativar').addEventListener('click', fecharModalInativar);
  document.getElementById('btn-confirmar-inativacao').addEventListener('click', confirmarInativacao);

  // Filtros e Pesquisa com Debounce
  let timerBusca = null;
  const inputPesquisa = document.getElementById('filtro-pesquisa');
  const btnLimpar = document.getElementById('btn-limpar-pesquisa');

  inputPesquisa.addEventListener('input', (e) => {
    const val = e.target.value;
    btnLimpar.classList.toggle('hidden', !val);
    clearTimeout(timerBusca);
    timerBusca = setTimeout(() => {
      Estado.filtros.termo = val;
      carregarColaboradores();
    }, 280);
  });

  btnLimpar.addEventListener('click', () => {
    inputPesquisa.value = '';
    btnLimpar.classList.add('hidden');
    Estado.filtros.termo = '';
    carregarColaboradores();
  });

  document.getElementById('filtro-situacao').addEventListener('change', (e) => {
    Estado.filtros.situacao = e.target.value;
    carregarColaboradores();
  });

  document.getElementById('filtro-setor').addEventListener('change', (e) => {
    Estado.filtros.setor = e.target.value;
    carregarColaboradores();
  });

  document.getElementById('btn-recarregar').addEventListener('click', carregarColaboradores);
  document.getElementById('btn-limpar-filtros').addEventListener('click', () => {
    inputPesquisa.value = '';
    btnLimpar.classList.add('hidden');
    document.getElementById('filtro-situacao').value = 'todos';
    document.getElementById('filtro-setor').value = '';
    Estado.filtros = { termo: '', situacao: 'todos', setor: '' };
    carregarColaboradores();
  });

  // Máscaras de Entrada no Formulário
  document.getElementById('campo-cpf').addEventListener('input', (e) => {
    e.target.value = mascaraCpf(e.target.value);
  });

  document.getElementById('campo-telefone').addEventListener('input', (e) => {
    e.target.value = mascaraTelefone(e.target.value);
  });

  document.getElementById('campo-cep').addEventListener('input', (e) => {
    e.target.value = mascaraCep(e.target.value);
  });

  document.getElementById('campo-salario').addEventListener('blur', (e) => {
    if (e.target.value) e.target.value = formatarMoeda(e.target.value);
  });
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  configurarEventos();
  carregarColaboradores();
});
