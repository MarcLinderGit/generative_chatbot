import numpy as np
import re
from test_model import encoder_model, decoder_model, num_decoder_tokens, num_encoder_tokens, input_features_dict, target_features_dict, reverse_target_features_dict, max_decoder_seq_length, max_encoder_seq_length

class ChatBot:
    def __init__(self):
        # Define negative commands and exit commands
        self.negative_commands = ["no", "no thanks", "not now", "maybe later"]
        self.exit_commands = ["exit", "quit", "bye", "goodbye"]

    def start_chat(self):
        print("Hello! I'm your chatbot. Would you like to chat about cats? (yes/no)")
        user_input = input().strip().lower()
        if user_input in self.negative_commands:
            print("Ok, goodbye!")
            return
        elif user_input not in self.exit_commands:
            self.chat(user_input)

    def make_exit(self, user_input):
        return any(exit_command in user_input for exit_command in self.exit_commands)

    def string_to_matrix(self, user_input):
        tokens = re.findall(r"[\w']+|[^\s\w]", user_input)
        user_input_matrix = np.zeros(
            (1, max_encoder_seq_length, num_encoder_tokens),
            dtype='float32'
        )

        for timestep, token in enumerate(tokens):
            if token in input_features_dict:
                user_input_matrix[0, timestep, input_features_dict[token]] = 1.

        return user_input_matrix

    def generate_response(self, user_input):
        user_input_matrix = self.string_to_matrix(user_input)
        states_value = encoder_model.predict(user_input_matrix)

        target_seq = np.zeros((1, 1, num_decoder_tokens))
        target_seq[0, 0, target_features_dict['<START>']] = 1.

        decoded_sentence = ''

        stop_condition = False
        while not stop_condition:
            output_tokens, hidden_state, cell_state = decoder_model.predict(
                [target_seq] + states_value)

            sampled_token_index = np.argmax(output_tokens[0, -1, :])
            sampled_token = reverse_target_features_dict[sampled_token_index]

            if sampled_token != '<START>' and sampled_token != '<END>':
                decoded_sentence += " " + sampled_token

            if sampled_token == '<END>' or len(decoded_sentence) > max_decoder_seq_length:
                stop_condition = True

            target_seq = np.zeros((1, 1, num_decoder_tokens))
            target_seq[0, 0, sampled_token_index] = 1.

            states_value = [hidden_state, cell_state]

        return decoded_sentence

    def chat(self, user_input):
        while not self.make_exit(user_input):
            response = self.generate_response(user_input)
            print("You:", user_input)
            print("Bot:", response)
            user_input = input().strip().lower()

if __name__ == "__main__":
    chatbot = ChatBot()
    chatbot.start_chat()
