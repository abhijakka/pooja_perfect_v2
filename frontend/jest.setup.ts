import "@testing-library/jest-dom";

// jsdom does not implement Element.scrollTo, which the chat panels call to stay
// pinned to the newest message. Stub it once here so every suite that renders a
// chat component works without repeating the setup.
if (!Element.prototype.scrollTo) {
	Element.prototype.scrollTo = jest.fn();
}
