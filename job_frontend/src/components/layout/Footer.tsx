export function Footer() {
  return (
    <footer className="border-t mt-auto py-6 bg-muted/30">
      <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
        <p>
          © {new Date().getFullYear()} JobAggregator. Data sourced from publicly
          available job boards.
        </p>
      </div>
    </footer>
  );
}
