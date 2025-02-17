#!/usr/bin/python3
"""
    states.py file in v1/views
"""
from flask import abort, Flask, jsonify, request, make_response
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.city import City
from models.user import User


@app_views.route("/cities/<city_id>/places", methods=["GET", "POST"], strict_slashes=False)
def handle_places(city_id):
    """
        Method to return a JSON representation of all states
    """
    city_by_id = storage.get(City, city_id)
    if city_by_id is None:
        abort(404, 'Not found')

    if request.method == 'GET':
        place_list = []
        for place in city_by_id.places:
            place_list.append(place.to_dict())
        return jsonify(place_list)

    elif request.method == 'POST':
        post = request.get_json()
        if post is None or type(post) != dict:
            return jsonify({'error': 'Not a JSON'}), 400
        elif post.get('name') is None:
            return jsonify({'error': 'Missing name'}), 400
        elif post.get('user_id') is None:
            return jsonify({'error': 'Missing user_id'}), 400

        user_id = post['user_id']

        user_by_id = storage.get(User, user_id)
        city_by_id = storage.get(City, city_id)

        if not user_by_id or not city_by_id:
            abort(404)

        new_place = Place(**post)
        new_place.save()
        return jsonify(new_place.to_dict()), 201


@app_views.route("/places/<place_id>", methods=["GET", "PUT", "DELETE"],
                 strict_slashes=False)
def handle_place_by_id(place_id):
    """
        Method to return a JSON representation of a state
    """
    place_by_id = storage.get(Place, place_id)
    if place_by_id is None:
        abort(404)
    elif request.method == 'GET':
        return jsonify(place_by_id.to_dict())
    elif request.method == 'DELETE':
        storage.delete(place_by_id)
        storage.save()
        return jsonify({}), 200
    elif request.method == 'PUT':
        put = request.get_json()
        if put is None or type(put) != dict:
            return jsonify({'message': 'Not a JSON'}), 400
        for key, value in put.items():
            if key not in ['id', 'created_at', 'updated_at']:
                setattr(place_by_id, key, value)
        storage.save()
        return jsonify(place_by_id.to_dict()), 200


@app_views.route('/places_search', methods=["POST"], strict_slashes=False)
def post_places_search():
    """searches for a place"""
    if request.get_json() is not None:
        params = request.get_json()
        states = params.get('states', [])
        cities = params.get('cities', [])
        amenities = params.get('amenities', [])
        amenity_objects = []
        for amenity_id in amenities:
            amenity = storage.get('Amenity', amenity_id)
            if amenity:
                amenity_objects.append(amenity)
        if states == cities == []:
            places = storage.all('Place').values()
        else:
            places = []
            for state_id in states:
                state = storage.get('State', state_id)
                state_cities = state.cities
                for city in state_cities:
                    if city.id not in cities:
                        cities.append(city.id)
            for city_id in cities:
                city = storage.get('City', city_id)
                for place in city.places:
                    places.append(place)
        confirmed_places = []
        for place in places:
            place_amenities = place.amenities
            confirmed_places.append(place.to_dict())
            for amenity in amenity_objects:
                if amenity not in place_amenities:
                    confirmed_places.pop()
                    break
        return jsonify(confirmed_places)
    else:
        return make_response(jsonify({'error': 'Not a JSON'}), 400)
