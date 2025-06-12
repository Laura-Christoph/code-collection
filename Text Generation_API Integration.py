import gradio as gr
from transformers import pipeline, GenerationConfig # Create a text generation pipeline


generator = pipeline("text-generation", model="gpt2")
config = GenerationConfig.from_pretrained("gpt2")
# The default config of GPT-2 is greedy decoding
# Generate text


def mockup(prompt, temperature, max_length, top_p):
    if temperature == 0:
        config.do_sample = False
    else:
        config.do_sample = True
        config.top_p = top_p
        config.temperature = temperature

    output = generator(prompt,
                    max_new_tokens=max_length,
                    generation_config=config,
                    )
    return output[0]['generated_text']


with gr.Blocks() as demo:
    # Dropdown menu for selecting the prompt if you don't feel creative. 
    dropdown_prompt_selector = gr.Dropdown(choices=["I love my life, but",
                                                    "In summer, I want to", 
                                                    "In my dreams, I", 
                                                    "I wish I knew"
                                                    ],
                                                    allow_custom_value=True, 
                                                    label="Prompt selector",
                                                    info="Choose a prompt or write your own!")

    # For now I choose the drop down menu instead of Textbox                                              
    # prompt = gr.Textbox(label="Prompt", placeholder="Prompt", lines=5, value="Write a tagline for an ice cream shop")
    output = gr.Textbox(label="Output")
    temp = gr.Slider(0, 2,1,label="temperature", info="The temperature of the sampling distribution")
    max_len = gr.Slider(1, 256,16, label="Maximum length", info="The maximum length of the output text")
    top_p = gr.Slider(0, 1,1, label="top position", info="The probability of sampling from the top n words")
    submit_btn = gr.Button("Submit")
    submit_btn.click(fn=mockup, inputs=[dropdown_prompt_selector,temp,max_len,top_p], outputs=output, api_name="submit")

demo.launch()