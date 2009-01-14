//
//  CategoryViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface CategoryViewController : UITableViewController
{
	NSMutableArray *categories;
}

- (IBAction)onAddCategory:(UIBarButtonItem *)button;

@end
