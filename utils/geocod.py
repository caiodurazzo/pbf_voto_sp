from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from geopy.point import Point

try:
    from tqdm.auto import tqdm
except ImportError:
    tqdm = None

BBOX_SP = (-24.01, -23.35, -46.83, -46.36)  # lat_min, lat_max, lon_min, lon_max

ABREVIACOES = {
    r"^AV\.?\s": "AVENIDA ",
    r"^R\.?\s": "RUA ",
    r"^AL\.?\s": "ALAMEDA ",
    r"^PC\.?\s|^PÇ\.?\s": "PRAÇA ",
    r"^TV\.?\s": "TRAVESSA ",
    r"^EST\.?\s": "ESTRADA ",
    r"^LGO\.?\s": "LARGO ",
    r"^VL\.?\s": "VIELA ",
}


def limpar_endereco(endereco: str, cidade: str = "São Paulo, SP, Brasil") -> tuple[str, str]:
    e = " ".join(str(endereco).upper().split())
    for padrao, novo in ABREVIACOES.items():
        e = re.sub(padrao, novo, e)

    rua, _, num = e.partition(",")
    rua = rua.strip().title()
    m = re.search(r"\d[\d\.]*", num)
    numero = m.group(0).replace(".", "") if m else ""

    completo = f"{rua}, {numero}" if numero else rua
    return f"{completo}, {cidade}", f"{rua}, {cidade}"


def _dentro_da_caixa(lat: float, lon: float, bbox) -> bool:
    lat_min, lat_max, lon_min, lon_max = bbox
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max


def geocodificar_df(
    df: pd.DataFrame,
    coluna: str,
    email: str,
    cidade: str = "São Paulo, SP, Brasil",
    cache_path: str | Path = "cache_geocodificacao.json",
    bbox: tuple | None = BBOX_SP,
    pais: str = "br",
    limite: int | None = None,
    refazer: tuple[str, ...] = (),
) -> pd.DataFrame:
    """
    Geocodifica os endereços únicos de df[coluna] e devolve uma cópia de df
    com as colunas lat, lon e status
    (ok | aproximado_rua | nao_encontrado | fora_da_caixa_revisar).
    """
    cache_path = Path(cache_path)
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    if refazer:
        cache = {k: v for k, v in cache.items() if v.get("status") not in refazer}

    extra: dict = {}
    if bbox:
        lat_min, lat_max, lon_min, lon_max = bbox
        extra = {
            "viewbox": [Point(lat_max, lon_min), Point(lat_min, lon_max)],
            "bounded": True,
        }

    geolocator = Nominatim(user_agent=f"geocod_utils ({email})", timeout=10)  # type: ignore[arg-type]
    geocode = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=1.1,
        max_retries=3,
        error_wait_seconds=5,
        swallow_exceptions=True,
    )

    unicos = df[coluna].dropna().unique()
    pendentes = [e for e in unicos if e not in cache]
    if limite is not None:
        pendentes = pendentes[:limite]
    print(f"{len(unicos)} endereços únicos | {len(pendentes)} a geocodificar")

    def salvar():
        cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    try:
        for i, end in enumerate(tqdm(pendentes) if tqdm else pendentes, 1):
            completo, so_rua = limpar_endereco(end, cidade)

            loc, status = geocode(completo, country_codes=pais, **extra), "ok"
            if loc is None:
                loc, status = geocode(so_rua, country_codes=pais, **extra), "aproximado_rua"

            if loc is None:
                cache[end] = {"lat": None, "lon": None, "status": "nao_encontrado"}
            else:
                if bbox and not _dentro_da_caixa(loc.latitude, loc.longitude, bbox):
                    status = "fora_da_caixa_revisar"
                cache[end] = {"lat": loc.latitude, "lon": loc.longitude, "status": status}

            if i % 25 == 0:
                salvar()
    finally:
        salvar()

    vazio = {"lat": None, "lon": None, "status": "pendente"}
    geo = pd.DataFrame([cache.get(e, vazio) for e in df[coluna]], index=df.index)
    return pd.concat([df, geo], axis=1)