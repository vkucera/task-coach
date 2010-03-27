//
//  SearchCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 27/03/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface SearchCell : UITableViewCell
{
	UISearchBar *searchBar;
}

@property (nonatomic, retain) IBOutlet UISearchBar *searchBar;

@end
