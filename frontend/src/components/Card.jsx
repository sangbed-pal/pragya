const Card = ({ feature, index }) => {
    return (
        <div
            key={index}
            className="bg-slate-800 p-6 rounded-2xl shadow-lg hover:scale-105 transform transition duration-300 border border-slate-700"
        >
            <h3 className="text-xl text-indigo-200 font-semibold mb-2">{feature.title}</h3>
            <p className="text-slate-300 text-sm">{feature.description}</p>
        </div>
    );
};

export default Card;