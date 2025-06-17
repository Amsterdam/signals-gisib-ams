import copy
import json
from datetime import datetime
from typing import List

from django.contrib.gis.geos import Point

from signals_gisib.gisib.api import post_collection_insert
from signals_gisib.models import CollectionItem, EPRCurative, Signal


def _tree_exists(tree_id: int) -> bool:
    return CollectionItem.objects.filter(
        gisib_id=tree_id,
        object_kind_name__iexact='Boom',
        raw_properties__Soortnaam__Description__istartswith='Quercus'
    ).exists()


def _get_tree_ids(extra_properties: List[dict]) -> List[int]:
    tree_ids = []
    for extra_property in extra_properties:
        if extra_property['id'] == 'extra_eikenprocessierups':
            answers = extra_property.get('answer', [])
            for answer in answers:
                if 'id' in answer and answer['id'] and _tree_exists(answer['id']):
                    tree_ids.append(answer['id'])
                else:
                    tree_ids.append(None)
    return list(set(tree_ids)) if tree_ids else []


def _translate_nest_size(extra_properties: List[dict]) -> int | None:
    _translation = {
        # 'signal_answer': 'gisib_answer'
        'Nest is zo groot als een tennisbal': 'Nest is zo groot als een tennisbal',
        'Nest is zo groot als een voetbal': 'Nest is zo groot als een voetbal',
        'Rupsen bedekken de stam als een deken': 'Rupsen bedekken de stam als een deken',
        'De rupsen in de boom hebben nog geen nest gevormd': 'De rupsen in de boom hebben nog geen nest gevormd',
    }

    signal_answer = None
    for extra_property in extra_properties:
        if extra_property['id'] == 'extra_nest_grootte':
            signal_answer = extra_property['answer']['label']
            break

    if signal_answer:
        try:
            collection_item = CollectionItem.objects.get(
                object_kind_name__iexact='Nestformaat', raw_properties__Description__iexact=_translation[signal_answer]
            )
            return collection_item.gisib_id
        except CollectionItem.DoesNotExist:
            return None
    return None


def _create_post_collection_insert_body(signal_id: int, signal_created_at: datetime,  signal_geometry: Point,
                                        nest_size: int | None, tree_id: int | None = None) -> dict:
    body = {
        'Properties': {
            'SIG Nummer melding': signal_id,
            'Datum melding': signal_created_at.strftime('%d-%m-%Y %H:%M'),
            'Nestformaat': nest_size,
        },
        'ObjectKindNaam': 'EPR Curatief'
    }

    if tree_id:
        body['Properties'].update({'Boom': tree_id})
    else:
        # Make a copy of the geometry and transform from 4326 (World Geodetic System, WGS84) to 28992 (Rijksdriehoek)
        point_28992 = copy.deepcopy(signal_geometry)
        point_28992.transform(28992)
        body.update({'Geometry': json.loads(point_28992.json)})

    return body


def create_epr_curative(signal: Signal) -> List[int]:
    nest_size = _translate_nest_size(signal.signal_extra_properties)
    tree_ids = _get_tree_ids(signal.signal_extra_properties)

    post_collection_insert_body_list = []
    if len(tree_ids) > 0:
        for tree_id in tree_ids:
            post_collection_insert_body_list.append(_create_post_collection_insert_body(
                signal_id=signal.signal_id,
                signal_geometry=signal.signal_geometry,
                signal_created_at=signal.signal_created_at,
                nest_size=nest_size,
                tree_id=tree_id,
            ))
    else:
        post_collection_insert_body_list.append(_create_post_collection_insert_body(
            signal_id=signal.signal_id,
            signal_geometry=signal.signal_geometry,
            signal_created_at=signal.signal_created_at,
            nest_size=nest_size,
        ))

    created_epr_curative_id_list = []
    for post_collection_insert_body in post_collection_insert_body_list:
        response = post_collection_insert(post_collection_insert_body)

        epr_curative = EPRCurative.objects.create(signal=signal,
                                                  gisib_id=response['Properties']['Id'],
                                                  original_request=post_collection_insert_body,
                                                  original_response=response)

        created_epr_curative_id_list.append(epr_curative.id)
    return created_epr_curative_id_list
