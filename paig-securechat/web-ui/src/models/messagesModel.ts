type Message = {
  content: string;
  created_on: string;
  type: string | null;
  message_uuid: string | null;
  source_metadata: string | null;
};

type Conversation = {
  conversation_uuid: string | null;
  title: string;
  messages: Message[];
  ai_application_name?: string;
};

//later move to different file

type AIApplicationResponse = {
  AI_application: AIApplication[];
};

type AIApplication = {
  name: string;
  display_name: string;
  description: string;
  default?: boolean;
  welcome_column1: {
    header: string;
    messages: string[];
  };
  welcome_column2: {
    header: string;
    messages: string[];
  };
};
