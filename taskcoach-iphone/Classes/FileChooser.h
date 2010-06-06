//
//  FileChooser.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CategoryViewController;

@interface FileChooser : UITableViewController
{
	NSFetchedResultsController *resultsCtrl;
	CategoryViewController *catCtrl;
}

- initWithController:(CategoryViewController *)ctrl;

@end
