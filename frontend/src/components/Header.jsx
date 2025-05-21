const Header = () => {
    return (
        <header className="p-4 fixed top-0 w-full shadow-md bg-slate-950 backdrop-blur-sm text-center">
                <h1
                    className="text-5xl font-normal text-white tracking-wider drop-shadow-md"
                    style={{
                        fontFamily: "'Great Vibes', cursive",
                        textShadow: "0 0 6px rgba(99, 102, 241, 0.6)",
                    }}
                >
                    Pragya
                </h1>
            </header>
    );
};

export default Header;