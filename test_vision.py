from src.vision import analyze_room


with open("test_room.jpg", "rb") as image_file:

    image_bytes = image_file.read()


result = analyze_room(
    image_bytes,
    "image/jpeg"
)


print(result.model_dump_json(indent=4))