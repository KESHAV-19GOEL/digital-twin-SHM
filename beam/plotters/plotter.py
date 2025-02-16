import os

from pathlib import Path
from tensorflow import keras
keras.backend.clear_session()

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import ListedColormap

class Plot:
    
    def __init__(self, graph,path):
        self.graph=graph    
        self.path=path
        if not os.path.exists(Path(self.path)):
            print("no path exist")
            os.mkdir(Path(self.path))
            
        
    def plot_history_all_together(self, figsize=(10, 7)):

        viridis_big = mpl.colormaps['Blues']
        newcmp = ListedColormap(viridis_big(np.linspace(0.1, 0.7, 128)))
        
        ############ history D ############
        
        hist = self.graph.hist_var
        hist_prob_D = self.graph.hist_d_state_prob.to_numpy()
        n_delta_steps = hist_prob_D.shape[1]//(self.graph.physical_asset.n_classes-1)

        index_estimated = np.array([np.where(self.graph.states_list == 
                            hist.d_state.to_numpy()[i])[0] for i in 
                            range(hist_prob_D.shape[0])])

        # non discretized
        index_truth = np.array([np.max([0.,(1+(int(hist.p_state.to_numpy()[i].split(';')[0])-1) * 6 \
                                + (float(hist.p_state.to_numpy()[i].split(';')[1])-0.3)/0.1)]) for i in \
                                range(hist_prob_D.shape[0])])

        index_pad_est = np.zeros((self.graph.physical_asset.n_classes-1,
                                hist_prob_D.shape[0]))
        index_pad_tru = np.zeros((self.graph.physical_asset.n_classes-1,
                                hist_prob_D.shape[0]))
        #n_regions x n_step x n_intervals
        hist_prob_pad = np.zeros((self.graph.physical_asset.n_classes-1,
                                hist_prob_D.shape[0],1+n_delta_steps))

        hist_prob_pad[:,:,0] = hist_prob_D[:,0]
        for i in range(1,hist_prob_D.shape[1]):
            zone = (i-1)//n_delta_steps
            hist_prob_pad[zone,:,i-(zone*n_delta_steps)] = hist_prob_D[:,i]

        for i in range(hist_prob_D.shape[0]):
            if index_estimated[i]!=0:
                zone = int((index_estimated[i]-1)//n_delta_steps)
                index_pad_est[zone,i] = index_estimated[i]-(zone*n_delta_steps)
            if int(hist.p_state.to_numpy()[i].split(';')[0])!=0:
                zone = int(hist.p_state.to_numpy()[i].split(';')[0])-1
                index_pad_tru[zone,i] = index_truth[i]-(zone*n_delta_steps)

        self.indices = [
            i for i, history in enumerate(index_pad_tru) if np.amax(history) > 0
        ]

        ############ history U ############
        
        hist_prob_U = self.graph.hist_actions_prob
        
        index_estimated = np.array([np.where(self.graph.actions_list == 
                            hist.current_action.to_numpy()[i])[0] for i in 
                            range(hist_prob_U.shape[0])])
        
        index_optimal = np.array([np.argmax(self.graph.planner.policy.T[:,np.where(
                    self.graph.states_list == hist.p_state_discrete.to_numpy()[i])[0]]) 
                    for i in range(hist_prob_U.shape[0])])
        
        if hist_prob_U.shape[1]==2:
            r=len(self.indices)*[1] + [0.5]
        if hist_prob_U.shape[1]==4:
            r=len(self.indices)*[1] + [0.8]
        
        plt.rc('font', size=19)
        fig, ax = plt.subplots(nrows=len(self.indices)+1, sharex=True, figsize=figsize,
                               height_ratios=r)
        
        
        for i, j in enumerate(self.indices):
            img1 = ax[i].pcolormesh(np.arange(hist_prob_pad[j].shape[0]),
                                   np.arange(hist_prob_pad[j].shape[1]), 
                                   hist_prob_pad[j].T, 
                                   shading='nearest', vmin=0., vmax=1., cmap=newcmp)

            ax[i].plot(np.arange(0, hist_prob_pad[j].shape[0], 1), index_pad_est[j],
                     color='red', alpha=0.7, linewidth=1.8)
            ax[i].plot(np.arange(0, hist_prob_pad[j].shape[0], 1), index_pad_tru[j],
                     color='black', alpha=0.7, linestyle='dashed', linewidth=1.8)

            ax[i].grid(linestyle='dotted')
            ax[i].set_xticks(np.arange(+.5, hist_prob_pad[j].shape[0]-0.5, 1));
            ax[i].set_yticks(np.arange(+.5, hist_prob_pad[j].shape[1]-0.5, 1));
            ax[i].set_xticklabels(labels=[]);
            ax[i].set_yticklabels(labels=[]);

            ax[i].set_xticks(np.arange(0, hist_prob_pad[j].shape[0], 5), minor=True);
            ax[i].set_yticks(np.arange(0, hist_prob_pad[j].shape[1], 1), minor=True);
            ax[i].set_xticklabels(list(map(str, np.arange(0, hist_prob_pad[j].shape[0], 5))),
                                  minor=True, 
                                  fontsize=18);
            ax[i].set_yticklabels(['No dmg', '', '$40\%$','','$60\%$','','$80\%$'],
                                  minor=True,
                                  fontsize=18);

            ax[i].set_ylabel(ylabel=f'$\delta(\Omega_{str(j+1)})$', labelpad=-18)
            
        i=len(self.indices)
        
        img2 = ax[i].pcolormesh(np.arange(hist_prob_U.shape[0]),
                            np.arange(hist_prob_U.shape[1]), 
                            hist_prob_U.T, 
                            shading='nearest', vmin=0., vmax=1., cmap=newcmp)
    
        ax[i].plot(np.arange(0,hist_prob_U.shape[0],1),index_estimated,
                  color='red', alpha=0.7, linewidth=1.8)
        
        ax[i].plot(np.arange(0,hist_prob_U.shape[0],1),index_optimal,
                  color='black', alpha=0.7, linestyle='dashed', linewidth=1.8)    
            
        ax[i].grid(linestyle='dotted')
        ax[i].set_xticks(np.arange(+.5, hist_prob_U.shape[0]-0.5, 1));
        ax[i].set_yticks(np.arange(+.5, hist_prob_U.shape[1]-0.5, 1));
        ax[i].set_xticklabels(labels=[]);
        ax[i].set_yticklabels(labels=[]);
        
        ax[i].set_xticks(np.arange(0, hist_prob_U.shape[0], 5), minor=True);
        ax[i].set_yticks(np.arange(0, hist_prob_U.shape[1], 1), minor=True);
        ax[i].set_xticklabels(list(map(str, np.arange(0, hist_prob_U.shape[0], 5))),
                           minor=True, 
                           fontsize=18);
        
        if hist_prob_U.shape[1]==2:
            ax[i].set_yticklabels(['DN', 'PM'], minor=True, fontsize=18);
            ax[0].legend(['Digital twin', 'Ground truth'], ncol=1, loc='upper right')
        if hist_prob_U.shape[1]==4:
            ax[i].set_yticklabels(['DN', 'PM', 'MI', 'MA'], minor=True, fontsize=18);
            ax[0].legend(['Digital twin', 'Ground truth'], loc='upper center', bbox_to_anchor=(0.5, 1.6), ncol=2)
        
        plt.ylabel(ylabel='Actions',labelpad=15);
        plt.xlabel('Time step $t$');
        
        if hist_prob_U.shape[1]==2:
            cbar = fig.colorbar(img1, ax=ax[0:len(self.indices)], orientation='vertical', pad=0.03, aspect=30);
        if hist_prob_U.shape[1]==4:
            cbar = fig.colorbar(img1, ax=ax[0:len(self.indices)], orientation='vertical', pad=0.03, aspect=47)
            
        cbar.set_label('$P \,(D_t | D_{t-1}, D^{\mathtt{NN}}_{t}, U^{\mathtt{A}}_{t-1}=u^{\mathtt{A}}_{t-1})$')

        cbar = fig.colorbar(img2, ax=ax[len(self.indices)], orientation='vertical', pad=0.03, aspect=7, ticks=[0.0, 0.5, 1.0])
        cbar.set_label('$P \, (U^{\mathtt{P}}_t|D_t)$')
        
        # To save the plot at the desired location
        # plt.savefig(Path(self.path + '/history.pdf'))
        
        # To show the plot on the screen
        plt.show()


    def plot_prediction_all_together(self, n_steps=1, n_samples=1000, figsize=(10, 5)):
        viridis_big = mpl.colormaps['Blues']
        newcmp = ListedColormap(viridis_big(np.linspace(0.1, 0.7, 128)))

        predict_D, predict_U = self.graph.predict(n_steps=n_steps, n_samples=n_samples) 

        predict_D = predict_D.to_numpy()
        predict_U = predict_U.to_numpy()
        
        n_delta_steps = predict_D.shape[1]//(self.graph.physical_asset.n_classes-1)

        pred_prob_pad = np.zeros((self.graph.physical_asset.n_classes-1,
                                  predict_D.shape[0],1+n_delta_steps))

        pred_prob_pad[:,:,0] = predict_D[:,0]
        for i in range(1,predict_D.shape[1]):
            zone = (i-1)//n_delta_steps
            pred_prob_pad[zone,:,i-(zone*n_delta_steps)] = predict_D[:,i]
            
        plt.rc('font', size=19)
        fig, ax = plt.subplots(nrows=2, sharex=True, figsize=figsize, height_ratios=[1, 0.4])
        
        img = ax[0].pcolormesh(np.arange(pred_prob_pad[self.indices[-1]].shape[0]),
                               np.arange(pred_prob_pad[self.indices[-1]].shape[1]), 
                               pred_prob_pad[self.indices[-1]].T, 
                               shading='nearest', vmin=0., vmax=1., cmap=newcmp)

        ax[0].grid(linestyle='dotted')
        ax[0].set_xticks(np.arange(+.5, pred_prob_pad[5].shape[0]-0.5, 1));
        ax[0].set_yticks(np.arange(+.5, pred_prob_pad[5].shape[1]-0.5, 1));
        ax[0].set_xticklabels(labels=[]);
        ax[0].set_yticklabels(labels=[]);
    
        ax[0].set_xticks(np.arange(0, pred_prob_pad[5].shape[0], 5), minor=True);
        ax[0].set_yticks(np.arange(0, pred_prob_pad[5].shape[1], 1), minor=True);
        ax[0].set_xticklabels(list(map(str, np.arange(0, pred_prob_pad[5].shape[0], 5))), minor=True, fontsize=18);
        ax[0].set_yticklabels(['No dmg','$30\%$','$40\%$','$50\%$','$60\%$','$70\%$','$80\%$'], minor=True, fontsize=18);
            
        ax[0].set_ylabel(ylabel=f'$\delta(\Omega_{str(self.indices[-1]+1)})$', labelpad=-18)

        plt.xlabel('Time step $t$');
        
        cbar = fig.colorbar(img, ax=ax[0], orientation='vertical', pad=0.03, aspect=17)
        cbar.set_label('$P \, (D_t|D_{t-1},U^{\mathtt{P}}_{t-1})$')


        img2 = ax[1].pcolormesh(np.arange(predict_U.shape[0]),
                                np.arange(predict_U.shape[1]), 
                                predict_U.T, 
                                shading='nearest', vmin=0., vmax=1., cmap=newcmp)

        ax[1].grid(linestyle='dotted')
        ax[1].set_xticks(np.arange(+.5, predict_U.shape[0]-0.5, 1));
        ax[1].set_yticks(np.arange(+.5, predict_U.shape[1]-0.5, 1));
        ax[1].set_xticklabels(labels=[]);
        ax[1].set_yticklabels(labels=[]);

        ax[1].set_xticks(np.arange(0, predict_U.shape[0], 5), minor=True);
        ax[1].set_yticks(np.arange(0, predict_U.shape[1], 1), minor=True);
        ax[1].set_xticklabels(list(map(str, np.arange(0, predict_U.shape[0], 5))), minor=True, fontsize=18);
        
        if predict_U.shape[1]==2:
            ax[1].set_yticklabels(['DN', 'PM'], minor=True, fontsize=18);
        if predict_U.shape[1]==4:
            ax[1].set_yticklabels(['DN', 'PM', 'MI', 'MA'], minor=True, fontsize=18);

        plt.xlabel('Time step $t$');
        plt.ylabel('Actions', labelpad=15);

        cbar = fig.colorbar(img2, ax=ax[1], orientation='vertical', pad=0.03, aspect=7, ticks=[0.0, 0.5, 1.0])
        cbar.ax.set_yticklabels(['0.00', '0.50', '1.00'])
        cbar.set_label('$P \, (U^{\mathtt{P}}_t|D_t)$')
        
        # To save the plot at the desired location
        # plt.savefig(Path(self.path + '/predictions.pdf'))
        
        # To show the plot on the screen
        plt.show()

    def temp_plot_confusion_matrix(self,conf_mat_dt):
        # viridis_big = mpl.colormaps['viridis']
        # newcmp = ListedColormap(viridis_big(np.linspace(0.1, 0.7, 128)))
        # plt.rc('font', size=19)



        # Plotting the matrix as an image
        plt.imshow(conf_mat_dt, cmap='viridis', interpolation='nearest')
        
        # Adding a colorbar to indicate intensity values
        plt.colorbar(label="Intensity")
        
        # Adding labels and title
        plt.title("Intensity Plot")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        
        # Show the plot
        plt.show()
            
    def plot_confusion_matrix(self,conf_mat_dt):
        viridis_big = mpl.colormaps['Blues']

        plt.rc('font', size=13, family='serif')

        fig, ax = plt.subplots()

        # Plotting the matrix as an image
        plt.imshow(conf_mat_dt, cmap=viridis_big, interpolation='nearest')
        
        # Adding a colorbar to indicate intensity values
        colorbar = plt.colorbar(label="Classification accuracy",orientation='vertical', pad=0.03, aspect=30)

        # Customize the colorbar ticks to display percentages
        ticks = colorbar.get_ticks()  # Get the default ticks
        percent_ticks = [f"{int(tick * 100)}%" for tick in ticks]  # Convert to percentage format
        
        # Apply the new tick labels
        colorbar.set_ticks(ticks)
        colorbar.set_ticklabels(percent_ticks)
        
        # Specify gridline positions (indices where lines are to be added)
        vertical_lines = [0.5,6.5,12.5,18.5,24.5,30.5,36.5,42.5 ]  # Columns after which to add vertical gridlines
        horizontal_lines = [0.5,6.5,12.5,18.5,24.5,30.5,36.5,42.5]  # Rows after which to add horizontal gridlines
        
        # Add vertical grid lines
        for x in vertical_lines:
            ax.vlines(x, 0, conf_mat_dt.shape[0], colors='black',alpha=0.5, linestyles='dashed', linewidth=1.1)
        
        # Add horizontal grid lines
        for y in horizontal_lines:
            ax.hlines(y, 0, conf_mat_dt.shape[1], colors='black',alpha=0.7, linestyles='dotted', linewidth=1.1)

        # Define specific y-tick positions and labels
        ytick_positions = [3.5,9.5,15.5,21.5,27.5,33.5,39.5]  # Positions on the y-axis
        ytick_labels = [f'$\Omega_{str(1)}$', f'$\Omega_{str(2)}$',f'$\Omega_{str(3)}$', f'$\Omega_{str(4)}$',f'$\Omega_{str(5)}$',f'$\Omega_{str(6)}$',f'$\Omega_{str(7)}$']  # Corresponding labels
       
        # Define specific x-tick positions and labels
        xtick_positions = [3.5,9.5,15.5,21.5,27.5,33.5,39.5]  # Positions on the y-axis
        xtick_labels = [f'$\Omega_{str(1)}$', f'$\Omega_{str(2)}$',f'$\Omega_{str(3)}$', f'$\Omega_{str(4)}$',f'$\Omega_{str(5)}$',f'$\Omega_{str(6)}$',f'$\Omega_{str(7)}$']  # Corresponding labels

        # Set y-ticks and their labels
        ax.set_yticks(ytick_positions)
        ax.set_yticklabels(ytick_labels)
        
        # Set x-ticks and their labels
        ax.set_xticks(xtick_positions)
        ax.set_xticklabels(xtick_labels)

        # Adding labels and title
        # plt.title("Confusion Matrix")
        plt.xlabel("Predicted state")
        plt.ylabel("Target state")
        
        # Save the plot at the desired location
        # plt.savefig(Path(self.path + '/Confusion_matrix.pdf'))
        
        # Show the plot
        plt.show()
    	
            