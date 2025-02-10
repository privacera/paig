import React, { useState } from "react";
import Tooltip from '@material-ui/core/Tooltip';
import Switch from '@material-ui/core/Switch';



const categoriesData = {
  suggested_categories: [
    { name: "Cybercrime", desc: "Security risks and vulnerabilities." },
    { name: "PII", desc: "Personally Identifiable Information protection." },
    { name: "RBAC", desc: "Role-Based Access Control policies." },
  ],
  all_categories: [
    { name: "Cybercrime", desc: "Security risks and vulnerabilities." },
    { name: "PII", desc: "Personally Identifiable Information protection." },
    { name: "RBAC", desc: "Role-Based Access Control policies." },
    { name: "Survey analysts", desc: "Analysis and insights from surveys." },
    { name: "Decision-Making Support", desc: "Enhancing decision quality." },
    { name: "Operational Efficiency", desc: "Improving workflow operations." },
  ],
};

const EvaluationCategories = () => {
  const [selectedCategories, setSelectedCategories] = useState(
    categoriesData.suggested_categories.map((c) => c.name)
  );
  const [showSuggested, setShowSuggested] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  const handleToggle = () => setShowSuggested(!showSuggested);

  const handleCheckboxChange = (category) => {
    setSelectedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  };

  const filteredCategories = (showSuggested
    ? categoriesData.suggested_categories
    : categoriesData.all_categories
  ).filter((c) => c.name.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="p-4 border rounded-md shadow-md bg-white w-full max-w-lg">
      <h2 className="text-lg font-semibold">Evaluation Categories</h2>
      <p className="text-sm text-gray-600">
        Select categories to focus on specific aspects of model performance.
      </p>

      <div className="flex items-center my-2">
        <span className="mr-2">Suggested filters</span>
        <Switch checked={showSuggested} onChange={handleToggle} />
      </div>

      <input
        type="text"
        placeholder="Search categories..."
        className="border p-2 w-full rounded-md mb-2"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      <div className="grid grid-cols-2 gap-2">
        {filteredCategories.map((category) => (
          <Tooltip key={category.name} title={category.desc} arrow>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedCategories.includes(category.name)}
                onChange={() => handleCheckboxChange(category.name)}
              />
              <span>{category.name}</span>
            </label>
          </Tooltip>
        ))}
      </div>
    </div>
  );
};

export default EvaluationCategories;
