import {IoCopyOutline} from "react-icons/io5";
import {positions} from "react-alert";
import {useAlert} from "react-alert";

export default function CopyButton({tweets}) {
  const alert = useAlert();
  function Clickcopy(text) {
    alert.success("Copied Text", {
      timeout: 2000,
      position: positions.TOP_CENTER,
    });

    navigator.clipboard.writeText(text);
  }

  return (
    <div>
      <button
        type="button"
        onClick={() => {
          Clickcopy(tweets.map((t) => t[0]).join("\n\n***\n\n"));
        }}
        className="border border-slate-500 hover:shadow-xl pointer-events-auto rounded p-2"
      >
        <div className="flex flex-row space-x-3">
          <IoCopyOutline
            size="14"
            className="text-gray-500 font-extralight my-auto"
          />
          <p className="text-xs">Copy Thread Text</p>
        </div>
      </button>
    </div>
  );
}
