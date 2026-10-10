from enum import Enum


class ConversationState(str, Enum):
    INTRO = "INTRO"
    PERMISSION = "PERMISSION"
    DISCOVERY = "DISCOVERY"
    PAIN_POINT = "PAIN_POINT"
    VALUE_PROPOSITION = "VALUE_PROPOSITION"
    QUALIFICATION = "QUALIFICATION"
    PRICING = "PRICING"
    DEMO = "DEMO"
    CALLBACK = "CALLBACK"
    END = "END"
    DO_NOT_CALL = "DO_NOT_CALL"


class ConversationManager:
    def __init__(self) -> None:
        self.state = ConversationState.INTRO

    def next_prompt(self) -> str:
        prompts = {
            ConversationState.INTRO: "నమస్కారం సార్/మేడమ్. నేను Gym OS నుంచి AI assistant గా మాట్లాడుతున్నాను. మీకు 30 seconds మాట్లాడే అవకాశం ఉందా?",
            ConversationState.PERMISSION: "మీరు ముందుకు వెళ్లాలని అనుకుంటే, నేను మీ gym ఎలా operate చేస్తున్నారో అడగడం ప్రారంభించవచ్చు.",
            ConversationState.DISCOVERY: "ప్రస్తుతం మీ gym members, attendance మరియు payments ఎలా manage చేస్తున్నారు?",
            ConversationState.PAIN_POINT: "ఆ process లో ఏ major problem ఉందో చెప్పగలరా? member follow-ups, pending payments, attendance tracking, లేదా staff coordination?",
            ConversationState.VALUE_PROPOSITION: "Gym OS లో members, attendance, payments మరియు follow-ups ఒకే dashboard లో manage చేయడం సులభం. ఇది మీ pain point కి relevant గా ఉంటుంది.",
            ConversationState.QUALIFICATION: "మీ gymకు real problem ఉందా? మీరు decision maker అయితే, demo రోజును discuss చేయవచ్చు.",
            ConversationState.PRICING: "ప్రస్తుతం early-access setup fee ₹3,000. మీకు удобно అయితే, founder చిన్న demo చూపించగలరు.",
            ConversationState.DEMO: "మీకు useful గా అనిపిస్తే మా founder మీకు ఒక చిన్న demo చూపించగలరు. ఏ సమయం convenient గా ఉంటుంది?",
            ConversationState.CALLBACK: "సరే, నేను మీకు follow-upకు suitable time అడగవచ్చు. మీకు మళ్లీ కాల్ చేయడానికి ఎప్పుడు సరిపోతుందో చెప్పండి.",
            ConversationState.END: "ధన్యవాదాలు. మీకు మీ convenience aligned time లో మేము contact చేస్తాము.",
            ConversationState.DO_NOT_CALL: "సరే, మీకు మేము future calls చేయము. మీ నంబర్ do-not-call list లో ఉంచాము.",
        }
        return prompts.get(self.state, prompts[ConversationState.INTRO])

    def update_state(self, user_input: str) -> ConversationState:
        value = (user_input or "").lower()
        if "don't call" in value or "do not call" in value or "remove my number" in value or "not interested" in value:
            self.state = ConversationState.DO_NOT_CALL
            return self.state
        if "demo" in value or "show" in value:
            self.state = ConversationState.DEMO
            return self.state
        if "price" in value or "3000" in value or "₹3,000" in value:
            self.state = ConversationState.PRICING
            return self.state
        if "excel" in value or "whatsapp" in value or "software" in value or "book" in value or "notebook" in value:
            self.state = ConversationState.PAIN_POINT
            return self.state
        if "yes" in value or "okay" in value or "sure" in value or "fine" in value:
            if self.state in {ConversationState.INTRO, ConversationState.PERMISSION}:
                self.state = ConversationState.DISCOVERY
                return self.state
        self.state = ConversationState.DISCOVERY
        return self.state
