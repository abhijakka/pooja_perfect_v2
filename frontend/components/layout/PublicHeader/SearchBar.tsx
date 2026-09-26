import type { FormEvent } from "react";
import Link from "next/link";
import type { StoreProduct } from "../../product/ProductCard/ProductGrid";
import { Icon } from "../../Icon";

type SearchBarProps = {
	query: string;
	suggestions: StoreProduct[];
	onQueryChange: (value: string) => void;
	onSearch: (event: FormEvent<HTMLFormElement>) => void;
};

export function SearchBar({ query, suggestions, onQueryChange, onSearch }: SearchBarProps) {
	return (
		<form className="search-box" onSubmit={onSearch}>
			<input
				value={query}
				onChange={(event) => onQueryChange(event.target.value)}
				type="search"
				placeholder="Search diyas, idols, incense, pooja kits..."
				aria-label="Search products"
			/>
			<button className="search-button" type="submit" aria-label="Search">
				<Icon name="search" />
			</button>
			{suggestions.length > 0 && (
				<div className="search-suggestions">
					<div className="search-suggestions__head">
						<strong>Products</strong>
						<span>{suggestions.length} results</span>
					</div>
					{suggestions.map((product) => (
						<Link className="search-suggestion" href={`/products/${product.slug}`} key={product.id}>
							<span className="search-suggestion-image">
								<img src={product.image} alt={product.name} />
							</span>
							<span className="search-suggestion-info">
								<strong className="search-suggestion-name">{product.name}</strong>
								<span className="search-suggestion-meta">
									<span>{product.categoryLabel}</span>
									<span aria-hidden="true">·</span>
									<strong className="search-suggestion-price">₹{product.price.toLocaleString("en-IN")}</strong>
								</span>
							</span>
							<span className="search-view-button">View</span>
						</Link>
					))}
				</div>
			)}
		</form>
	);
}
