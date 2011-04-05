//
//  TaskTableView.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface TaskTableView : UITableViewController <NSFetchedResultsControllerDelegate>
{
    NSFetchedResultsController *resultsCtrl;
}

- (void)reload;

@end
