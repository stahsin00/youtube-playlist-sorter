import openai


def get_openai_response(prompt, openai_api_key):
    try:
        openai.api_key = openai_api_key

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error: {e}")
        return None


def make_categories(titles, openai_api_key):
    try:
        prompt = ("Given the set of video titles, come up with playlist titles that all of "
                  "the videos can be categorized into. Try to be broad with the categories such "
                  "as \"Game Development\" or \"Art\" while limiting too much overlap between them. "
                  f"The video titles are as follows: {'; '.join(titles)}.")

        return get_openai_response(prompt, openai_api_key)
    except Exception as e:
        print(f"Error: {e}")
        return None


def place_in_category(snippet, categories_string, openai_api_key):
    try:
        prompt = (f"Given the following list of categories: [{categories_string}], "
                  "in which category would you place a video with the following info: "
                  f"The video title is '{snippet['title']}', and its description is '{snippet['description']}'. "
                  "Reply with only the category name and no other explanation.")

        return get_openai_response(prompt, openai_api_key)
    except Exception as e:
        print(f"Error: {e}")
        return None