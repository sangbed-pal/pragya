import { LuArrowRight } from "react-icons/lu";
import { Link } from "react-router";
import Card from "../components/Card.jsx";

const features = [
    {
        title: "Multilingual Summaries",
        description: "Submit YouTube URLs in any language and receive concise summaries in your preferred language.",
    },

    {
        title: "Conversational Insights",
        description: "Ask questions based on generated summaries — Pragya responds intelligently.",
    },

    {
        title: "Voice Input Support",
        description: "Speak your queries directly using the microphone for a hands-free experience.",
    },

    {
        title: "Voice Response Output",
        description: "Listen to Pragya's answers with seamless voice response integration.",
    }
];

const Home = () => {
    return (
        <div className="bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-white h-screen pt-10 overflow-y-auto scrollbar-thin scrollbar-thumb-indigo-400 scrollbar-track-transparent scrollbar-thumb-rounded-lg scrollbar-hover:scrollbar-thumb-indigo-300 scrollbar-active:scrollbar-thumb-indigo-400">
    
            <div>
                <video
                    className="w-full shadow-xl"
                    controls
                    autoPlay
                    muted
                    loop
                    src="/videos/video1.mp4"
                />
            </div>

            <section className="py-16 px-4 text-center">
                <h2 className="text-4xl font-medium mb-12">Why Choose Pragya?</h2>
                <div className="grid gap-8 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 max-w-6xl mx-auto">
                    {features.map((feature, index) => (
                        <Card index={index} feature={feature} />
                    ))}
                </div>
            </section>

            <div className="flex justify-center pb-14">
                <Link to="/chat">
                    <button className="flex items-center gap-2 text-xl px-10 py-6 rounded-full shadow-lg bg-gradient-to-r from-indigo-500 to-violet-600 text-white hover:scale-105 transition-transform cursor-pointer">
                        Get Started <LuArrowRight className="w-5 h-5" />
                    </button>
                </Link>
            </div>
        </div>
    );
};

export default Home;