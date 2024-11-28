# README

## Visão Geral

Algoritmo para execução do método que tem por objetivo obter uma medida indicadora de heterogeneidade em rochas. Inicialmente é feito o processo de divisão sistemática de imagens de amostras rochosas em subvolumes e o subsequente cálculo de atributos em cada subvolume. Em seguida a entropia é utilizada, por se tratar de uma medida estatística que indica a incerteza ou a quantidade de informação contida em uma variável aleatória. A metodologia envolve o particionamento da imagem em subcubos e o cálculo de características estatísticas diretamente dos valores de escala de cinza, explorando a relação entre a variação dos resultados e a presença de heterogeneidade.

## Requisitos

- Utilizar imagem fornecida no arquivo [Dockerfile](./Dockerfile). (Já consta na imagem do singularity em [run_sample.sh](./function/run_sample.sh) (sif="/nethome/drp/ia-drp/singularity/lab2m_ubu_11.10_cuda_11.8.0_devel_tensorflow_2.11.sif").

## Arquivos

- `schedule_jobs.sh`: _Script shell_para processar múltiplas imagens a partir de um arquivo CSV.
- `run_sample.sh`: _Script shell_ para cálculo da medida de heterogeneidade.
- `run_sample.py`: _Script python_ para processar imagens e calcular .
- `parser_utils.py`: Funções utilitárias para parseamento de argumentos do _shell_.
- `image_preprocessing_utils.py`: Funções para pré-processamento de imagens.
- `feature_calculation_utils.py`: Funções para cálculo de _features_ dentro de cada subvolume.
- `rank_calculation_utils.py`: Funções para cálculo de entropia e ranking de heterogeneidade.


## Execução

### Argumentos para execução

O script `run_sample.py` possui os seguintes argumentos:

- **`-sample_path`** (str): Caminho para o arquivo `.nc` da amostra (obrigatório).
- **`-features_folder`** (str): Caminho para o diretório onde as _features_ serão armazenadas.
- **`-output_folder`** (str): Diretório onde os resultados serão salvos.
- **`-data_entropy_path`** (str): Caminho para o CSV com dados de entropia previamente calculados.
- **`-data_rank_path`** (str): Caminho para o CSV com dados de ranking.
- **`-division_list`** (list): Lista de divisões (padrão: `[2,3,4,5,6,7,8,9,10]`).
- **`-contrast_adjustment_options`** (list): Lista de ajustes de contraste (padrão: `[True, False]`).
- **`-feature_list`** (list): _Features_ para calcular em cada subcubo (padrão: `['mean','std','kurtosis','variation coefficient']`).
- **`-z_ini`** (int ou None): Índice inicial no eixo Z (opcional).
- **`-z_fin`** (int ou None): Índice final no eixo Z (opcional).

### Preparação dos arquivos

Para submeter um job usando `sbatch`, siga estes passos:

- Copie este projeto para o seu local de preferência e atualize os caminhos em `run_sample.sh`.
  
```bash
cp -r /nethome/drp/ia-drp/luan_workspace/PetrophysicsFeatures /pasta/do/usuario
```

- Alterar: **/nethome/drp/ia-drp/luan_workspace:/home** no arquivo [run_sample](./function/run_sample.sh).
- Verificar que os arquivos CSV de **/nethome/drp/ia-drp/luan_workspace/PetrophysicsFeatures/features** estão na pasta features.

- Configurar parâmetros no arquivo [run_sample.sh](./function/run_sample.sh).
    Exemplo: `-contrast_adjustment_options true,false` para calcular medida com e sem ajuste de contraste.
    A conversão para lista [True, False] é feita dentro do código pela pelo [parser_utils.py](./function/parser_utils.py).

### Execução via `sbatch`:

- Múltiplos arquivos via CSV

```bash
sbatch schedule_jobs.sh samples_test.csv
```

- Arquivo único

```bash
sbatch run_sample.sh /caminho/para/nc 
```

- Arquivo único com z_ini e z_fin (opcional e temporário enquanto desenvolvemos o código para automatizar o corte na dimensão z). Caso não seja fornecido, é usado um threshold de 10% para definir z_min e z_max.

```bash
sbatch run_sample.sh /caminho/para/nc z_ini z_fin
```

Para rodar com e sem ajuste de contraste, alterar contrast_

### Execução importando função:

Caso opte por importar a função para executá-la diretamente no seu código:

```python
from run_sample import heterogeneity_rank

heterogeneity_rank(
    sample_path='/caminho/para/imagem_da_amostra.nc',
    features_folder = '/pasta/features'
    output_folder='/caminho/para/diretorio_de_saida',
    division_list=[2, 3, 4, 5, 6, 7, 8, 9, 10],
    contrast_adjustment_options=[True, False],
    feature_list=['mean', 'std', 'kurtosis', 'variation coefficient'],
    data_rank_path='/caminho/para/entropy_rank_results.csv',
    data_entropy_path='/caminho/para/entropy_results.csv',
    z_ini = None,
    z_fin = None
)
```

### Arquivos auxiliares

[Base de amostras com valores de entropia previamente calculados - cortes manuais, voidmean, rockmedian](./function/allfilesdata3D_newcuts.csv)

[Arquivo CSV de exemplo para teste da execução](./function/samples_test.csv)

- Observação: os valores de _voidmean_ e _rockmedian_ são aleatórios, acarretando uma pequena diferença nos valores a cada rodada (podemos fixar a _seed_).

### Exemplos de uso

1. Múltiplas imagens via arquivo CSV


```
sbatch schedule_jobs.sh samples_test.csv
```

#### Job scheduler

- [log](./function/logs/Result-schedule_jobs.5561975.out)

##### Output RJS749_T012338V_LIMPA_P_58500nm_23102024_235247

- [Info](./function/output/RJS749_T012338V_LIMPA_P_58500nm_23102024_235247/info_RJS749_T012338V_LIMPA_P_58500nm.csv)
- [Features](./function/output/RJS749_T012338V_LIMPA_P_58500nm_23102024_235247/features_RJS749_T012338V_LIMPA_P_58500nm.csv)
- [Entropy](./function/output/RJS749_T012338V_LIMPA_P_58500nm_23102024_235247/entropy_RJS749_T012338V_LIMPA_P_58500nm.csv)
- [Rank](./function/output/RJS749_T012338V_LIMPA_P_58500nm_23102024_235247/entropy_RJS749_T012338V_LIMPA_P_58500nm.csv)
- [log](./function/logs/Result-run_sample.5561976.out)

##### Output RJS749D_T012329H_LIMPA_P_58500nm_23102024_235300

- [Info](./function/output/RJS749D_T012329H_LIMPA_P_58500nm_23102024_235300/info_RJS749D_T012329H_LIMPA_P_58500nm.csv)
- [Features](./function/output/RJS749D_T012329H_LIMPA_P_58500nm_23102024_235300/features_RJS749D_T012329H_LIMPA_P_58500nm.csv)
- [Entropy](./function/output/RJS749D_T012329H_LIMPA_P_58500nm_23102024_235300/entropy_RJS749D_T012329H_LIMPA_P_58500nm.csv)
- [Rank](./function/output/RJS749D_T012329H_LIMPA_P_58500nm_23102024_235300/entropy_RJS749D_T012329H_LIMPA_P_58500nm.csv)
- [log](./function/logs/Result-run_sample.5561977.out)

2. Imagem única sem arquivo CSV - Informando cortes no eixo Z selecionados manualmente (opcional)

#### Sem job scheduler

```
sbatch run_sample.sh /data/RJS749D_T012329H_LIMPA_P_58500nm.nc 60 490
```

##### Output RJS749D_T012329H_LIMPA_P_58500nm_23102024_235417

- [Info](./function/output/RJS749D_T012329H_LIMPA_P_58500nm_23102024_235417/info_RJS749D_T012329H_LIMPA_P_58500nm.csv)
- [Features](./function/output/RJS749D_T012329H_LIMPA_P_58500nm_23102024_235417/features_RJS749D_T012329H_LIMPA_P_58500nm.csv)
- [Entropy](./function/output/RJS749D_T012329H_LIMPA_P_58500nm_23102024_235417/entropy_RJS749D_T012329H_LIMPA_P_58500nm.csv)
- [Rank](./function/output/RJS749D_T012329H_LIMPA_P_58500nm_23102024_235417/rank_RJS749D_T012329H_LIMPA_P_58500nm.csv)
- [log](./function/logs/Result-run_sample.5561978.out)

3. Imagem única sem arquivo CSV - Informando cortes inválidos

```
sbatch run_sample.sh /data/RJS749D_T012329H_LIMPA_P_58500nm.nc 100 300
```
- [log](./function/logs/Result-run_sample.5561979.out)
