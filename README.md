# README

## Visão Geral

Algoritmo para execução do método que tem por objetivo obter uma medida indicadora de heterogeneidade em rochas. Inicialmente é feito o processo de divisão sistemática de imagens de amostras rochosas em subvolumes e o subsequente cálculo de atributos em cada subvolume. Em seguida a entropia é utilizada, por se tratar de uma medida estatística que indica a incerteza ou a quantidade de informação contida em uma variável aleatória. A metodologia envolve o particionamento da imagem em subcubos e o cálculo de características estatísticas diretamente dos valores de escala de cinza, explorando a relação entre a variação dos resultados e a presença de heterogeneidade.

## Requisitos

- Utilizar imagem fornecida no arquivo [Dockerfile](./Dockerfile). (Já consta na imagem do singularity em [run_sample.sh](./function/run_sample.sh) (sif="/nethome/drp/ia-drp/singularity/lab2m_ubu_11.10_cuda_11.8.0_devel_tensorflow_2.11.sif").

## Arquivos

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

### Execução importando função:

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

[Base de amostras com valores de entropia previamente calculados - cortes manuais, voidmean, rockmedian]

- Observação: os valores de _voidmean_ e _rockmedian_ são aleatórios, acarretando uma pequena diferença nos valores a cada rodada (podemos fixar a _seed_).
